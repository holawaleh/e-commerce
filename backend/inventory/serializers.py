# inventory/serializers.py

from rest_framework import serializers
from domains.models import (
    Product,
    HotelProduct,
    PharmacyProduct,
    RetailProduct,
    AgricultureProduct,
    ElectronicsProduct,
    FashionProduct,
    FoodBeverageProduct,
    AutoPartsProduct,
)


# ─── BASE SERIALIZER ─────────────────────────────────────────────
# Fields that every domain shares.
class ProductBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "serial_no" "description",
            "price",
            "cost_price",
            "sku",
            "image",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ─── DOMAIN SERIALIZERS ──────────────────────────────────────────
# Each one inherits the base fields and appends its own.
# Meta.fields uses list concatenation: base fields + domain fields.


class HotelProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = HotelProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "room_type",
            "max_guests",
            "amenities",
            "is_available",
        ]


class PharmacyProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = PharmacyProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "manufacturer",
            "expiry_date",
            "batch_number",
            "category",
            "barcode",
        ]


class RetailProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = RetailProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "brand",
            "category",
            "size",
            "color",
            "weight",
            "barcode",
        ]


class AgricultureProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = AgricultureProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "product_type",
            "unit_of_measure",
            "harvest_date",
            "origin",
        ]


class ElectronicsProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = ElectronicsProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "brand",
            "model_number",
            "warranty_months",
            "specifications",
            "serial_number",
        ]


class FashionProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = FashionProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "brand",
            "category",
            "size",
            "color",
            "material",
        ]


class FoodBeverageProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = FoodBeverageProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "category",
            "expiry_date",
            "weight_grams",
            "volume_ml",
            "is_organic",
            "nutritional_info",
        ]


class AutoPartsProductSerializer(ProductBaseSerializer):
    class Meta(ProductBaseSerializer.Meta):
        model = AutoPartsProduct
        fields = ProductBaseSerializer.Meta.fields + [
            "brand",
            "part_number",
            "compatible_vehicles",
            "category",
            "warranty_months",
        ]


# ─── SERIALIZER FACTORY ──────────────────────────────────────────
# The ViewSet calls this with the tenant's domain string.
# It returns the correct serializer class — no if/elif chains needed.
DOMAIN_SERIALIZER_MAP = {
    "hotel_tourism": HotelProductSerializer,
    "pharmacy": PharmacyProductSerializer,
    "retail": RetailProductSerializer,
    "agriculture": AgricultureProductSerializer,
    "electronics": ElectronicsProductSerializer,
    "fashion": FashionProductSerializer,
    "food_beverage": FoodBeverageProductSerializer,
    "auto_parts": AutoPartsProductSerializer,
}


def get_serializer_for_domain(domain: str):
    """Returns the serializer class for a given domain. Falls back to base."""
    return DOMAIN_SERIALIZER_MAP.get(domain, ProductBaseSerializer)
