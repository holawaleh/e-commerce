# inventory/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet,
    CategoryViewSet,
    ProductViewSet,
    StockMovementViewSet,
    StockAlertViewSet,
)

router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"stock-movements", StockMovementViewSet, basename="stock-movement")
router.register(r"stock-alerts", StockAlertViewSet, basename="stock-alert")

urlpatterns = [
    path("", include(router.urls)),
]


# ============================================================
# inventory/admin.py
# ============================================================

from django.contrib import admin
from .models import Supplier, Category, Product, StockMovement, StockAlert


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "business",
        "contact_person",
        "phone",
        "email",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "business", "created_at"]
    search_fields = ["name", "contact_person", "email", "phone"]
    readonly_fields = ["created_by", "created_at", "updated_at"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "business", "parent", "created_at"]
    list_filter = ["business", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sku",
        "business",
        "category",
        "current_quantity",
        "selling_price",
        "is_active",
    ]
    list_filter = ["is_active", "business", "category", "tracking_type", "created_at"]
    search_fields = ["name", "sku", "description", "barcode"]
    readonly_fields = ["current_quantity", "created_by", "created_at", "updated_at"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "business",
                    "name",
                    "description",
                    "sku",
                    "category",
                    "supplier",
                )
            },
        ),
        ("Pricing", {"fields": ("cost_price", "selling_price")}),
        (
            "Stock Management",
            {
                "fields": (
                    "tracking_type",
                    "current_quantity",
                    "reorder_level",
                    "reorder_quantity",
                    "unit_of_measure",
                )
            },
        ),
        (
            "Additional Info",
            {"fields": ("barcode", "warranty_period_days", "is_active")},
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "movement_type",
        "quantity",
        "balance_after",
        "performed_by",
        "timestamp",
    ]
    list_filter = ["movement_type", "business", "timestamp"]
    search_fields = ["product__name", "product__sku", "reference_number"]
    readonly_fields = ["balance_after", "performed_by", "timestamp"]
    date_hierarchy = "timestamp"


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ["product", "alert_type", "is_resolved", "created_at", "resolved_at"]
    list_filter = ["alert_type", "is_resolved", "business", "created_at"]
    search_fields = ["product__name", "product__sku"]
    readonly_fields = ["created_at"]


# ============================================================
# inventory/signals.py
# ============================================================

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, StockMovement, StockAlert


@receiver(post_save, sender=Product)
def check_stock_alerts(sender, instance, created, **kwargs):
    """
    Create stock alerts when product is low or out of stock
    """
    if not created:  # Only for updates
        # Check for out of stock
        if instance.current_quantity == 0:
            StockAlert.objects.get_or_create(
                product=instance,
                business=instance.business,
                alert_type="OUT_OF_STOCK",
                is_resolved=False,
                defaults={"alert_type": "OUT_OF_STOCK"},
            )
        # Check for low stock
        elif (
            instance.current_quantity <= instance.reorder_level
            and instance.reorder_level > 0
        ):
            StockAlert.objects.get_or_create(
                product=instance,
                business=instance.business,
                alert_type="LOW_STOCK",
                is_resolved=False,
                defaults={"alert_type": "LOW_STOCK"},
            )
        else:
            # Resolve alerts if stock is back to normal
            StockAlert.objects.filter(
                product=instance,
                is_resolved=False,
                alert_type__in=["LOW_STOCK", "OUT_OF_STOCK"],
            ).update(is_resolved=True)


# ============================================================
# inventory/apps.py
# ============================================================

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"

    def ready(self):
        import inventory.signals  # Import signals when app is ready
