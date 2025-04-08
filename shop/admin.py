from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
    Coupon,
    CouponUsage,
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "featured", "order")
    list_filter = ("featured", "parent")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("featured", "order")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "price",
        "sale_price",
        "is_active",
        "in_stock",
        "featured",
    )
    list_filter = ("is_active", "in_stock", "featured", "categories")
    search_fields = ("name", "description", "sku")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "sale_price", "is_active", "in_stock", "featured")
    inlines = [ProductImageInline, ProductVariantInline]
    filter_horizontal = ("categories",)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_id", "created_at", "count", "total")
    search_fields = ("user__email", "session_id")
    inlines = [CartItemInline]
    readonly_fields = ("created_at", "updated_at")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "variant",
        "product_name",
        "variant_name",
        "price",
        "quantity",
        "subtotal",
    )


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "full_name",
        "status",
        "payment_status",
        "total",
        "created_at",
    )
    list_filter = ("status", "payment_status")
    search_fields = ("order_number", "full_name", "email")
    readonly_fields = ("order_number", "subtotal", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
    fieldsets = (
        ("Customer Info", {"fields": ("user", "full_name", "email", "phone")}),
        (
            "Shipping Details",
            {
                "fields": (
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            "Order Details",
            {
                "fields": (
                    "order_number",
                    "status",
                    "payment_status",
                    "shipping_cost",
                    "tax_amount",
                    "coupon",
                    "discount_amount",
                    "subtotal",
                    "total",
                )
            },
        ),
        (
            "Extra Info",
            {
                "fields": (
                    "order_notes",
                    "tracking_number",
                    "ip_address",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved")
    search_fields = ("title", "body", "user__email", "product__name")
    list_editable = ("is_approved",)


class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "active",
        "valid_from",
        "valid_to",
        "times_used",
    )
    list_filter = ("active", "discount_type")
    search_fields = ("code",)
    list_editable = ("active",)


class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "order", "used_at")
    list_filter = ("used_at",)
    search_fields = ("coupon__code", "user__email", "order__order_number")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(CouponUsage, CouponUsageAdmin)
