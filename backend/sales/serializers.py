# sales/serializers.py

from rest_framework import serializers
from .models import Order, OrderLineItem


class OrderLineItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderLineItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "line_total",
        ]
        read_only_fields = ["id", "line_total"]


# ── Read serializer: used for GET (list / retrieve) ──
class OrderSerializer(serializers.ModelSerializer):
    line_items = OrderLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "customer_name",
            "customer_email",
            "customer_phone",
            "notes",
            "subtotal",
            "discount",
            "total",
            "line_items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "subtotal", "total", "created_at", "updated_at"]


# ── Write serializer: used for POST (create) ──
# Line items are writable here so they're created with the order.
class OrderCreateSerializer(serializers.ModelSerializer):
    line_items = OrderLineItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "customer_name",
            "customer_email",
            "customer_phone",
            "notes",
            "discount",
            "line_items",
        ]

    def validate_line_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "An order must have at least one line item."
            )
        return value

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items")
        order = Order.objects.create(**validated_data)

        for item_data in line_items_data:
            product = item_data["product"]
            # Snapshot the product's current price at order time
            item_data.setdefault("unit_price", product.price)
            OrderLineItem.objects.create(order=order, **item_data)

        order.recalculate_totals()
        return order
