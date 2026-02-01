# domains/models.py
#
# ─── WHY MULTI-TABLE INHERITANCE (MTI) ───────────────────────────
# Each domain needs different fields on a product.
# MTI solves this cleanly:
#
#   Product (base table)          ← name, price, tenant — shared by ALL
#     ├── HotelProduct            ← room_type, max_guests — hotel only
#     ├── PharmacyProduct         ← dosage, expiry_date — pharmacy only
#     └── RetailProduct           ← brand, color, size — retail only
#         ... etc
#
# Django creates a SEPARATE table for each child and links it to
# the Product table with an automatic one-to-one key.
# No nullable bloat. No duplicated columns. Clean tables.
# ─────────────────────────────────────────────────────────────────

from django.db import models
from logaccess.models import Tenant


# ─── BASE PRODUCT ────────────────────────────────────────────────
# Concrete model (NOT abstract) — gets its own DB table.
# Every child inherits these columns automatically.
class Product(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sku = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.tenant.business_name}"

    @property
    def profit_margin(self):
        if self.cost_price and self.cost_price > 0:
            return round(float((self.price - self.cost_price) / self.price * 100), 2)
        return 0.0


# ─── HOTEL & TOURISM ─────────────────────────────────────────────
class HotelProduct(Product):
    room_type = models.CharField(max_length=100, blank=True)
    max_guests = models.PositiveIntegerField(default=1)
    beds = models.PositiveIntegerField(default=1)
    check_in_policy = models.TextField(blank=True)
    amenities = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hotel / Tourism Product"
        verbose_name_plural = "Hotel / Tourism Products"


# ─── PHARMACY ────────────────────────────────────────────────────
class PharmacyProduct(Product):
    manufacturer = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    dosage_form = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    is_prescription_required = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Pharmacy Product"
        verbose_name_plural = "Pharmacy Products"


# ─── RETAIL ──────────────────────────────────────────────────────
class RetailProduct(Product):
    brand = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)

    class Meta:
        verbose_name = "Retail Product"
        verbose_name_plural = "Retail Products"


# ─── AGRICULTURE ─────────────────────────────────────────────────
class AgricultureProduct(Product):
    product_type = models.CharField(max_length=100, blank=True)
    unit_of_measure = models.CharField(max_length=50, blank=True)
    season = models.CharField(max_length=50, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    origin = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Agriculture Product"
        verbose_name_plural = "Agriculture Products"


# ─── ELECTRONICS ─────────────────────────────────────────────────
class ElectronicsProduct(Product):
    brand = models.CharField(max_length=150, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    warranty_months = models.PositiveIntegerField(default=0)
    specifications = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True, unique=True, null=True)

    class Meta:
        verbose_name = "Electronics Product"
        verbose_name_plural = "Electronics Products"


# ─── FASHION & APPAREL ───────────────────────────────────────────
class FashionProduct(Product):
    brand = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    season = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Fashion Product"
        verbose_name_plural = "Fashion Products"


# ─── FOOD & BEVERAGE ─────────────────────────────────────────────
class FoodBeverageProduct(Product):
    category = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    weight_grams = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    volume_ml = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    is_organic = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=True)
    nutritional_info = models.TextField(blank=True)

    class Meta:
        verbose_name = "Food & Beverage Product"
        verbose_name_plural = "Food & Beverage Products"


# ─── AUTOMOBILE PARTS ────────────────────────────────────────────
class AutoPartsProduct(Product):
    brand = models.CharField(max_length=150, blank=True)
    part_number = models.CharField(max_length=100, blank=True)
    compatible_vehicles = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    warranty_months = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Auto Parts Product"
        verbose_name_plural = "Auto Parts Products"


# ─── DOMAIN → MODEL REGISTRY ─────────────────────────────────────
# Maps the domain string (from Tenant.domain) to the correct model.
# Views and serializers use this to pick the right class at runtime.
DOMAIN_MODEL_MAP = {
    "hotel_tourism": HotelProduct,
    "pharmacy": PharmacyProduct,
    "retail": RetailProduct,
    "agriculture": AgricultureProduct,
    "electronics": ElectronicsProduct,
    "fashion": FashionProduct,
    "food_beverage": FoodBeverageProduct,
    "auto_parts": AutoPartsProduct,
}


def get_product_model_for_tenant(tenant):
    """Given a Tenant, return its domain-specific Product model class."""
    model = DOMAIN_MODEL_MAP.get(tenant.domain)
    if model is None:
        raise ValueError(f"No product model for domain: {tenant.domain}")
    return model
