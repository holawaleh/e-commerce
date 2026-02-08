# inventory/serializers.py

from rest_framework import serializers
from .models import Supplier, Category, Product, StockMovement, StockAlert
from user_management.serializers import UserSerializer


class SupplierSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "business",
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "notes",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate(self, data):
        # Ensure supplier name is unique within the business
        business = data.get("business")
        name = data.get("name")

        if self.instance:
            # Update case
            if (
                Supplier.objects.filter(business=business, name=name)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError(
                    {
                        "name": "A supplier with this name already exists in your business"
                    }
                )
        else:
            # Create case
            if Supplier.objects.filter(business=business, name=name).exists():
                raise serializers.ValidationError(
                    {
                        "name": "A supplier with this name already exists in your business"
                    }
                )

        return data


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "business",
            "name",
            "description",
            "parent",
            "subcategories",
            "product_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "category_name",
            "supplier_name",
            "cost_price",
            "selling_price",
            "current_quantity",
            "reorder_level",
            "is_low_stock",
            "tracking_type",
            "is_active",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product details"""

    category = CategorySerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    profit_margin = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "business",
            "name",
            "description",
            "sku",
            "category",
            "supplier",
            "cost_price",
            "selling_price",
            "profit_margin",
            "tracking_type",
            "current_quantity",
            "reorder_level",
            "reorder_quantity",
            "is_low_stock",
            "unit_of_measure",
            "barcode",
            "warranty_period_days",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "current_quantity",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        # Validate selling price is greater than cost price
        cost_price = data.get(
            "cost_price", self.instance.cost_price if self.instance else 0
        )
        selling_price = data.get(
            "selling_price", self.instance.selling_price if self.instance else 0
        )

        if selling_price < cost_price:
            raise serializers.ValidationError(
                {
                    "selling_price": "Selling price should be greater than or equal to cost price"
                }
            )

        return data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""

    category_id = serializers.UUIDField(
        write_only=True, required=False, allow_null=True
    )
    supplier_id = serializers.UUIDField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            "business",
            "name",
            "description",
            "sku",
            "category_id",
            "supplier_id",
            "cost_price",
            "selling_price",
            "tracking_type",
            "reorder_level",
            "reorder_quantity",
            "unit_of_measure",
            "barcode",
            "warranty_period_days",
            "is_active",
        ]

    def validate_sku(self, value):
        business = self.context["request"].data.get("business")

        if self.instance:
            # Update case
            if (
                Product.objects.filter(business=business, sku=value)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError(
                    "A product with this SKU already exists in your business"
                )
        else:
            # Create case
            if Product.objects.filter(business=business, sku=value).exists():
                raise serializers.ValidationError(
                    "A product with this SKU already exists in your business"
                )

        return value

    def create(self, validated_data):
        category_id = validated_data.pop("category_id", None)
        supplier_id = validated_data.pop("supplier_id", None)

        if category_id:
            validated_data["category_id"] = category_id
        if supplier_id:
            validated_data["supplier_id"] = supplier_id

        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop("category_id", None)
        supplier_id = validated_data.pop("supplier_id", None)

        if category_id:
            validated_data["category_id"] = category_id
        if supplier_id:
            validated_data["supplier_id"] = supplier_id

        return super().update(instance, validated_data)


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    performed_by_name = serializers.SerializerMethodField()
    movement_type_display = serializers.CharField(
        source="get_movement_type_display", read_only=True
    )

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "business",
            "movement_type",
            "movement_type_display",
            "quantity",
            "balance_after",
            "serial_number",
            "batch_number",
            "supply_date",
            "expiry_date",
            "reason",
            "reference_number",
            "performed_by",
            "performed_by_name",
            "timestamp",
        ]
        read_only_fields = ["id", "balance_after", "performed_by", "timestamp"]

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return (
                f"{obj.performed_by.first_name} {obj.performed_by.last_name}"
                if obj.performed_by.first_name
                else obj.performed_by.email
            )
        return "System"

    def validate(self, data):
        product = data.get("product")
        movement_type = data.get("movement_type")
        quantity = data.get("quantity")
        serial_number = data.get("serial_number", "")
        batch_number = data.get("batch_number", "")
        reason = data.get("reason", "")

        # Validate quantity is positive
        if quantity <= 0:
            raise serializers.ValidationError(
                {"quantity": "Quantity must be greater than 0"}
            )

        # Validate tracking numbers based on product tracking_type
        if product.tracking_type == Product.SERIAL and not serial_number:
            raise serializers.ValidationError(
                {"serial_number": "Serial number is required for this product"}
            )

        if product.tracking_type == Product.BATCH and not batch_number:
            raise serializers.ValidationError(
                {"batch_number": "Batch number is required for this product"}
            )

        if product.tracking_type == Product.BOTH:
            if not serial_number or not batch_number:
                raise serializers.ValidationError(
                    {
                        "tracking": "Both serial number and batch number are required for this product"
                    }
                )

        # Validate reason is provided for specific movement types
        if movement_type in [
            StockMovement.RETURN,
            StockMovement.DAMAGE,
            StockMovement.THEFT,
            StockMovement.ADJUSTMENT,
        ]:
            if not reason:
                raise serializers.ValidationError(
                    {"reason": f"Reason is required for {movement_type} movements"}
                )

        # Validate sufficient stock for outgoing movements
        if movement_type in [
            StockMovement.SALE,
            StockMovement.DAMAGE,
            StockMovement.THEFT,
            StockMovement.TRANSFER_OUT,
        ]:
            if product.current_quantity < quantity:
                raise serializers.ValidationError(
                    {
                        "quantity": f"Insufficient stock. Available: {product.current_quantity}, Requested: {quantity}"
                    }
                )

        return data

    def create(self, validated_data):
        validated_data["performed_by"] = self.context["request"].user
        return super().create(validated_data)


class StockAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    current_quantity = serializers.IntegerField(
        source="product.current_quantity", read_only=True
    )
    reorder_level = serializers.IntegerField(
        source="product.reorder_level", read_only=True
    )

    class Meta:
        model = StockAlert
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "business",
            "alert_type",
            "current_quantity",
            "reorder_level",
            "is_resolved",
            "resolved_at",
            "resolved_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
