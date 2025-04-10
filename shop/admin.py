from django.contrib import admin
from django.contrib import messages
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
    list_display = ("name", "parent", "featured", "order", "has_product_type")
    list_filter = ("featured", "parent")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("featured", "order")
    actions = ["sync_to_product_type"]

    def has_product_type(self, obj):
        return obj.product_type is not None

    has_product_type.boolean = True
    has_product_type.short_description = "In Bloom"

    def sync_to_product_type(self, request, queryset):
        """Admin action to sync selected categories to ProductType in bloom"""
        from bloom.models import ProductType

        created_count = 0
        updated_count = 0
        error_count = 0

        for category in queryset:
            # Skip child categories (only sync top-level)
            if category.parent is not None:
                continue

            try:
                if category.product_type:
                    # Update existing ProductType
                    product_type = category.product_type
                    product_type._skip_category_signal = True
                    product_type.name = category.name
                    product_type.save()
                    updated_count += 1
                else:
                    # Create new ProductType
                    product_type = ProductType.objects.create(name=category.name)

                    # Link to category
                    category._skip_product_type_signal = True
                    category.product_type = product_type
                    category.save(update_fields=["product_type"])
                    created_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error processing {category.name}: {str(e)}",
                    level=messages.ERROR,
                )
                error_count += 1

        # Show summary message
        self.message_user(
            request,
            f"Sync complete: {created_count} ProductTypes created, {updated_count} updated, {error_count} errors.",
            level=messages.SUCCESS if error_count == 0 else messages.WARNING,
        )

    sync_to_product_type.short_description = (
        "Sync selected categories to bloom ProductType"
    )


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
        "has_bloom_product",
    )
    list_filter = ("is_active", "in_stock", "featured", "categories")
    search_fields = ("name", "description", "sku")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "sale_price", "is_active", "in_stock", "featured")
    inlines = [ProductImageInline, ProductVariantInline]
    filter_horizontal = ("categories",)
    actions = ["update_stock_from_bloom", "show_bloom_product_info"]

    def has_bloom_product(self, obj):
        return hasattr(obj, "bloom_product_link") and obj.bloom_product_link is not None

    has_bloom_product.boolean = True
    has_bloom_product.short_description = "In Bloom"

    def update_stock_from_bloom(self, request, queryset):
        """Admin action to update stock quantities based on availability in bloom"""
        updated_count = 0

        for product in queryset:
            if hasattr(product, "bloom_product_link") and product.bloom_product_link:
                # Set a default stock quantity for products that exist in bloom
                product.stock_quantity = max(product.stock_quantity, 10)
                product.in_stock = True
                product.save(update_fields=["stock_quantity", "in_stock"])
                updated_count += 1

        if updated_count:
            self.message_user(
                request,
                f"Updated stock for {updated_count} products.",
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No products were updated. Make sure products are linked to bloom products.",
                level=messages.WARNING,
            )

    update_stock_from_bloom.short_description = "Update stock from bloom"

    def show_bloom_product_info(self, request, queryset):
        """Admin action to show information about linked bloom products"""
        bloom_count = 0
        missing_count = 0

        for product in queryset:
            if hasattr(product, "bloom_product_link") and product.bloom_product_link:
                bloom_product = product.bloom_product_link
                bloom_count += 1
                self.message_user(
                    request,
                    f"Product '{product.name}' is linked to bloom product '{bloom_product.name}' "
                    f"(SKU: {bloom_product.sku}, Price: ${bloom_product.price})",
                    level=messages.INFO,
                )
            else:
                missing_count += 1
                self.message_user(
                    request,
                    f"Product '{product.name}' is not linked to any bloom product.",
                    level=messages.WARNING,
                )

        self.message_user(
            request,
            f"Found {bloom_count} linked bloom products and {missing_count} unlinked products.",
            level=messages.SUCCESS if bloom_count > 0 else messages.WARNING,
        )

    show_bloom_product_info.short_description = "Show bloom product info"


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
