from django.shortcuts import render
from django.db import models

# Create your views here.
# inventory/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import Supplier, Category, Product, StockMovement, StockAlert
from .serializers import (
    SupplierSerializer,
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    StockMovementSerializer,
    StockAlertSerializer,
)
from user_management.permissions import HasBusinessPermission
from user_management.models import StaffMember


class InventoryPermission(HasBusinessPermission):
    """Check if user has inventory management permission"""

    permission_required = "can_manage_inventory"


class SupplierViewSet(viewsets.ModelViewSet):
    """CRUD operations for suppliers"""

    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "contact_person", "email", "phone"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        # Get suppliers for businesses where user has inventory permission
        user = self.request.user
        user_businesses = StaffMember.objects.filter(
            user=user, is_active=True, role__can_manage_inventory=True
        ).values_list("business_id", flat=True)

        queryset = Supplier.objects.filter(business_id__in=user_businesses)

        # Filter by business if provided
        business_id = self.request.query_params.get("business")
        if business_id:
            queryset = queryset.filter(business_id=business_id)

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD operations for categories"""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        user = self.request.user
        user_businesses = StaffMember.objects.filter(
            user=user, is_active=True, role__can_manage_inventory=True
        ).values_list("business_id", flat=True)

        queryset = Category.objects.filter(business_id__in=user_businesses)

        # Filter by business
        business_id = self.request.query_params.get("business")
        if business_id:
            queryset = queryset.filter(business_id=business_id)

        # Filter top-level categories only
        parent_only = self.request.query_params.get("parent_only")
        if parent_only == "true":
            queryset = queryset.filter(parent__isnull=True)

        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD operations for products"""

    permission_classes = [IsAuthenticated, InventoryPermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "sku", "description", "barcode"]
    ordering_fields = ["name", "sku", "current_quantity", "selling_price", "created_at"]
    ordering = ["name"]
    filterset_fields = ["category", "supplier", "is_active", "tracking_type"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        user = self.request.user
        user_businesses = StaffMember.objects.filter(
            user=user, is_active=True, role__can_manage_inventory=True
        ).values_list("business_id", flat=True)

        queryset = Product.objects.filter(
            business_id__in=user_businesses
        ).select_related("category", "supplier", "created_by")

        # Filter by business
        business_id = self.request.query_params.get("business")
        if business_id:
            queryset = queryset.filter(business_id=business_id)

        # Filter low stock products
        low_stock = self.request.query_params.get("low_stock")
        if low_stock == "true":
            queryset = queryset.filter(current_quantity__lte=models.F("reorder_level"))

        # Filter out of stock
        out_of_stock = self.request.query_params.get("out_of_stock")
        if out_of_stock == "true":
            queryset = queryset.filter(current_quantity=0)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def stock_history(self, request, pk=None):
        """Get stock movement history for a product"""
        product = self.get_object()
        movements = StockMovement.objects.filter(product=product).select_related(
            "performed_by"
        )

        # Pagination
        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = StockMovementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def recalculate_stock(self, request, pk=None):
        """Recalculate stock from movements (admin function)"""
        product = self.get_object()
        result = StockMovement.recalculate_stock(product)

        if result["fixed"]:
            return Response(
                {
                    "message": "Stock quantity corrected",
                    "old_quantity": result["old_quantity"],
                    "new_quantity": result["new_quantity"],
                }
            )
        else:
            return Response(
                {
                    "message": "Stock quantity is accurate",
                    "current_quantity": result["current_quantity"],
                }
            )

    @action(detail=False, methods=["get"])
    def low_stock_report(self, request):
        """Get list of low stock products"""
        business_id = request.query_params.get("business")
        if not business_id:
            return Response(
                {"error": "business parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        low_stock_products = Product.objects.filter(
            business_id=business_id,
            is_active=True,
            current_quantity__lte=models.F("reorder_level"),
        ).select_related("category", "supplier")

        serializer = ProductListSerializer(low_stock_products, many=True)
        return Response(
            {"count": low_stock_products.count(), "products": serializer.data}
        )

    @action(detail=False, methods=["get"])
    def inventory_value(self, request):
        """Calculate total inventory value"""
        business_id = request.query_params.get("business")
        if not business_id:
            return Response(
                {"error": "business parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = Product.objects.filter(business_id=business_id, is_active=True)

        total_cost_value = sum(p.cost_price * p.current_quantity for p in products)
        total_selling_value = sum(
            p.selling_price * p.current_quantity for p in products
        )
        potential_profit = total_selling_value - total_cost_value

        return Response(
            {
                "total_products": products.count(),
                "total_units": sum(p.current_quantity for p in products),
                "total_cost_value": total_cost_value,
                "total_selling_value": total_selling_value,
                "potential_profit": potential_profit,
            }
        )


class StockMovementViewSet(viewsets.ModelViewSet):
    """CRUD operations for stock movements"""

    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["product", "movement_type", "performed_by"]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        user = self.request.user
        user_businesses = StaffMember.objects.filter(
            user=user, is_active=True, role__can_manage_inventory=True
        ).values_list("business_id", flat=True)

        queryset = StockMovement.objects.filter(
            business_id__in=user_businesses
        ).select_related("product", "performed_by")

        # Filter by business
        business_id = self.request.query_params.get("business")
        if business_id:
            queryset = queryset.filter(business_id=business_id)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

    @action(detail=False, methods=["get"])
    def movement_summary(self, request):
        """Get summary of movements by type"""
        business_id = request.query_params.get("business")
        if not business_id:
            return Response(
                {"error": "business parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        movements = StockMovement.objects.filter(business_id=business_id)

        # Filter by date range if provided
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            movements = movements.filter(timestamp__gte=start_date)
        if end_date:
            movements = movements.filter(timestamp__lte=end_date)

        summary = movements.values("movement_type").annotate(
            total_movements=Count("id"), total_quantity=Sum("quantity")
        )

        return Response(summary)


class StockAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view for stock alerts"""

    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["alert_type", "is_resolved"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        user_businesses = StaffMember.objects.filter(
            user=user, is_active=True, role__can_manage_inventory=True
        ).values_list("business_id", flat=True)

        queryset = StockAlert.objects.filter(
            business_id__in=user_businesses
        ).select_related("product", "resolved_by")

        # Filter by business
        business_id = self.request.query_params.get("business")
        if business_id:
            queryset = queryset.filter(business_id=business_id)

        return queryset

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Mark alert as resolved"""
        alert = self.get_object()

        if alert.is_resolved:
            return Response(
                {"error": "Alert is already resolved"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()

        return Response({"message": "Alert resolved successfully"})
