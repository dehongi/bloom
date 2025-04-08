from django.contrib import admin
from .models import (
    Customer,
    Occasion,
    ProductType,
    Product,
    DeliveryMethod,
    Order,
    OrderItem,
    CustomField,
    OrderStatus,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class CustomFieldInline(admin.TabularInline):
    model = CustomField
    extra = 1


class OrderStatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 0
    readonly_fields = ["timestamp"]
    can_delete = False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "city", "country")
    search_fields = ("name", "email", "phone")
    list_filter = ("country", "state", "city")


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "product_type")
    list_filter = ("product_type", "occasions")
    search_fields = ("name", "sku", "description")
    filter_horizontal = ("occasions",)


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "customer",
        "order_date",
        "shipment_date",
        "status",
        "total",
    )
    list_filter = ("status", "order_date", "shipment_date")
    search_fields = (
        "reference_number",
        "salesorder_number",
        "customer__name",
        "shipping_address",
    )
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "order_date"
    inlines = [OrderItemInline, CustomFieldInline, OrderStatusInline]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "reference_number",
                    "salesorder_number",
                    "customer",
                    "order_date",
                    "shipment_date",
                    "status",
                )
            },
        ),
        (
            "Shipping Information",
            {
                "fields": (
                    "delivery_method",
                    "shipping_charge",
                    "recipient_name",
                    "recipient_phone",
                    "shipping_address",
                    "shipping_city",
                    "shipping_state",
                    "shipping_country",
                    "shipping_postal_code",
                )
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "subtotal",
                    "discount_type",
                    "discount_percentage",
                    "discount_value",
                    "is_discount_before_tax",
                    "tax_amount",
                    "total",
                )
            },
        ),
        (
            "Additional Information",
            {"fields": ("notes", "occasion", "message", "created_at", "updated_at")},
        ),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "name", "price", "quantity")
    list_filter = ("order__status",)
    search_fields = ("order__reference_number", "name")


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ("order", "field_id", "value")
    list_filter = ("field_id",)
    search_fields = ("order__reference_number", "field_id", "value")


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "timestamp", "updated_by")
    list_filter = ("status", "timestamp")
    search_fields = ("order__reference_number", "notes")
    readonly_fields = ["timestamp"]
    date_hierarchy = "timestamp"
