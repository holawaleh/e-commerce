# sales/models.py

import uuid
from django.db import models
from logaccess.models import Tenant, User
from domains.models import Product


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="orders")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    # Customer info
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    # Totals
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id.hex[:8]} — {self.customer_name} — {self.get_status_display()}"

    def recalculate_totals(self):
        """Recompute subtotal and total from current line items."""
        self.subtotal = sum(item.line_total for item in self.line_items.all())
        self.total = max(self.subtotal - self.discount, 0)
        self.save(update_fields=["subtotal", "total", "updated_at"])


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="line_items"
    )
    # FK to BASE Product — works for any domain child because of MTI
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_lines"
    )
    quantity = models.PositiveIntegerField(default=1)
    # Price snapshot at the time the order was placed
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ {self.unit_price}"

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
