# inventory/models.py

from django.db import models
from django.contrib.auth import get_user_model
from user_management.models import Business
import uuid

User = get_user_model()


class Supplier(models.Model):
    """Supplier information for products"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="suppliers"
    )
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_suppliers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suppliers"
        unique_together = ["business", "name"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.business.name}"


class Category(models.Model):
    """Product categories for organization"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "Categories"
        unique_together = ["business", "name", "parent"]
        ordering = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    """Product/Item in inventory"""

    # Tracking type choices
    NONE = "NONE"
    SERIAL = "SERIAL"
    BATCH = "BATCH"
    BOTH = "BOTH"

    TRACKING_CHOICES = [
        (NONE, "No Tracking"),
        (SERIAL, "Serial Number Only"),
        (BATCH, "Batch Number Only"),
        (BOTH, "Serial & Batch Number"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=100, blank=True, help_text="Stock Keeping Unit")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # Pricing
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Purchase price from supplier"
    )
    selling_price = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Price to sell to customers"
    )

    # Tracking configuration
    tracking_type = models.CharField(
        max_length=20, choices=TRACKING_CHOICES, default=NONE
    )

    # Stock information (for quick access - updated by StockMovement)
    current_quantity = models.IntegerField(
        default=0, help_text="Current stock quantity (auto-calculated)"
    )
    reorder_level = models.IntegerField(
        default=0, help_text="Minimum quantity before reorder alert"
    )
    reorder_quantity = models.IntegerField(
        default=0, help_text="Quantity to reorder when stock is low"
    )

    # Product metadata
    unit_of_measure = models.CharField(
        max_length=50, default="piece", help_text="e.g., piece, kg, liter, box"
    )
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    warranty_period_days = models.IntegerField(
        null=True, blank=True, help_text="Warranty period in days"
    )

    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_products"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        unique_together = ["business", "sku"]
        ordering = ["name"]
        indexes = [
            models.Index(fields=["business", "is_active"]),
            models.Index(fields=["barcode"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        """Check if stock is below reorder level"""
        return self.current_quantity <= self.reorder_level

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0


class StockMovement(models.Model):
    """Track all stock movements for audit trail"""

    # Movement types
    STOCK_IN = "STOCK_IN"
    SALE = "SALE"
    RETURN = "RETURN"
    DAMAGE = "DAMAGE"
    THEFT = "THEFT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"

    MOVEMENT_TYPES = [
        (STOCK_IN, "Stock In (Supplier)"),
        (SALE, "Sale"),
        (RETURN, "Customer Return"),
        (DAMAGE, "Damaged/Spoiled"),
        (THEFT, "Lost/Stolen"),
        (ADJUSTMENT, "Manual Adjustment"),
        (TRANSFER_OUT, "Transfer Out"),
        (TRANSFER_IN, "Transfer In"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="movements"
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="stock_movements"
    )

    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(
        help_text="Positive for increase, negative for decrease"
    )

    # Balance after this movement
    balance_after = models.IntegerField(help_text="Stock quantity after this movement")

    # Tracking details (optional based on product.tracking_type)
    serial_number = models.CharField(max_length=100, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)

    # Date information
    supply_date = models.DateField(
        null=True, blank=True, help_text="Date received from supplier"
    )
    expiry_date = models.DateField(
        null=True, blank=True, help_text="Product expiry date"
    )

    # Metadata
    reason = models.TextField(
        blank=True,
        help_text="Reason for movement (required for returns, damage, theft)",
    )
    reference_number = models.CharField(
        max_length=100, blank=True, help_text="Invoice/PO/Transfer reference"
    )

    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="stock_movements"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "stock_movements"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["product", "-timestamp"]),
            models.Index(fields=["business", "-timestamp"]),
            models.Index(fields=["movement_type", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} - {self.quantity} units"

    def save(self, *args, **kwargs):
        """Override save to update product current_quantity"""
        is_new = self._state.adding

        if is_new:
            # Calculate balance after this movement
            if self.movement_type in [self.STOCK_IN, self.RETURN, self.TRANSFER_IN]:
                # Positive movements (increase stock)
                self.quantity = abs(self.quantity)
                self.balance_after = self.product.current_quantity + self.quantity
            else:
                # Negative movements (decrease stock)
                self.quantity = abs(self.quantity)
                self.balance_after = self.product.current_quantity - self.quantity

            # Update product current_quantity
            self.product.current_quantity = self.balance_after
            self.product.save(update_fields=["current_quantity", "updated_at"])

        super().save(*args, **kwargs)

    @classmethod
    def recalculate_stock(cls, product):
        """
        Recalculate stock from all movements (for verification/correction)
        This is your "truth source" calculation
        """
        movements = cls.objects.filter(product=product).order_by("timestamp")

        calculated_quantity = 0
        for movement in movements:
            if movement.movement_type in [cls.STOCK_IN, cls.RETURN, cls.TRANSFER_IN]:
                calculated_quantity += movement.quantity
            else:
                calculated_quantity -= movement.quantity

        # Update product if there's a discrepancy
        if product.current_quantity != calculated_quantity:
            product.current_quantity = calculated_quantity
            product.save(update_fields=["current_quantity"])

            return {
                "fixed": True,
                "old_quantity": product.current_quantity,
                "new_quantity": calculated_quantity,
            }

        return {"fixed": False, "current_quantity": calculated_quantity}


class StockAlert(models.Model):
    """Track low stock alerts"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="alerts"
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="stock_alerts"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ("LOW_STOCK", "Low Stock"),
            ("OUT_OF_STOCK", "Out of Stock"),
            ("EXPIRING_SOON", "Expiring Soon"),
        ],
    )
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "stock_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name}"
