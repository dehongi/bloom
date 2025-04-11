from django.contrib import admin
from django.contrib import messages
from django.utils.text import slugify
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
    Employee,
    EmployeeOrderAssignment,
)
from shop.models import Product as ShopProduct, Category
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html


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
    list_display = ("name", "has_shop_category")
    search_fields = ("name",)
    actions = ["sync_to_category"]

    def has_shop_category(self, obj):
        return hasattr(obj, "shop_category") and obj.shop_category is not None

    has_shop_category.boolean = True
    has_shop_category.short_description = "In Shop"

    def sync_to_category(self, request, queryset):
        """Admin action to sync selected ProductTypes to Categories in shop"""
        from shop.models import Category

        created_count = 0
        updated_count = 0
        error_count = 0

        for product_type in queryset:
            try:
                # Check if already has a category
                if (
                    hasattr(product_type, "shop_category")
                    and product_type.shop_category
                ):
                    # Update existing category
                    category = product_type.shop_category
                    category._skip_product_type_signal = True
                    category.name = product_type.name
                    category.save()
                    updated_count += 1
                else:
                    # Create new category
                    category = Category.objects.create(
                        name=product_type.name,
                        slug=slugify(product_type.name),
                        product_type=product_type,
                        _skip_product_type_signal=True,
                    )
                    created_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error processing {product_type.name}: {str(e)}",
                    level=messages.ERROR,
                )
                error_count += 1

        # Show summary message
        self.message_user(
            request,
            f"Sync complete: {created_count} Categories created, {updated_count} updated, {error_count} errors.",
            level=messages.SUCCESS if error_count == 0 else messages.WARNING,
        )

    sync_to_category.short_description = "Sync selected product types to shop Category"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "product_type", "has_shop_product")
    list_filter = ("product_type", "occasions")
    search_fields = ("name", "sku", "description")
    filter_horizontal = ("occasions",)
    actions = ["sync_to_shop"]

    def has_shop_product(self, obj):
        return bool(obj.shop_product)

    has_shop_product.boolean = True
    has_shop_product.short_description = "In Shop"

    def sync_to_shop(self, request, queryset):
        """Admin action to sync selected bloom products to shop products"""
        created_count = 0
        updated_count = 0
        error_count = 0

        for bloom_product in queryset:
            try:
                if bloom_product.shop_product:
                    # Update existing shop product
                    shop_product = bloom_product.shop_product
                    shop_product.name = bloom_product.name
                    shop_product.description = (
                        bloom_product.description or shop_product.description
                    )
                    shop_product.price = bloom_product.price
                    shop_product.sku = bloom_product.sku
                    shop_product.save()
                    updated_count += 1
                else:
                    # Try to find a default category
                    default_category = None
                    if bloom_product.product_type:
                        default_category = Category.objects.filter(
                            name__iexact=bloom_product.product_type.name
                        ).first()

                    # If not found, try to match with an occasion
                    if not default_category and bloom_product.occasions.exists():
                        occasion_name = bloom_product.occasions.first().name
                        default_category = Category.objects.filter(
                            name__iexact=occasion_name
                        ).first()

                    # If still not found, use the first category
                    if not default_category:
                        default_category = Category.objects.first()

                        # If no categories exist, create a default one
                        if not default_category:
                            default_category = Category.objects.create(
                                name="Flowers",
                                slug="flowers",
                                description="Flower arrangements and bouquets",
                            )

                    # Create a unique slug
                    slug = slugify(bloom_product.name)
                    counter = 1
                    original_slug = slug

                    # Ensure slug is unique
                    while ShopProduct.objects.filter(slug=slug).exists():
                        slug = f"{original_slug}-{counter}"
                        counter += 1

                    # Create shop product
                    shop_product = ShopProduct.objects.create(
                        name=bloom_product.name,
                        slug=slug,
                        sku=bloom_product.sku,
                        description=bloom_product.description
                        or f"Beautiful {bloom_product.name}",
                        price=bloom_product.price,
                        stock_quantity=10,  # Default initial stock
                        is_active=True,
                        in_stock=True,
                        meta_title=bloom_product.name,
                        meta_description=f"Order {bloom_product.name} from our flower shop",
                    )

                    # Add to default category
                    if default_category:
                        shop_product.categories.add(default_category)

                    # Link back to bloom product
                    bloom_product._skip_shop_product_signal = True
                    bloom_product.shop_product = shop_product
                    bloom_product.save(update_fields=["shop_product"])

                    created_count += 1

            except Exception as e:
                self.message_user(
                    request,
                    f"Error processing {bloom_product.name}: {str(e)}",
                    level=messages.ERROR,
                )
                error_count += 1

        # Show summary message
        self.message_user(
            request,
            f"Sync complete: {created_count} products created, {updated_count} updated, {error_count} errors.",
            level=messages.SUCCESS if error_count == 0 else messages.WARNING,
        )

    sync_to_shop.short_description = "Sync selected products to shop"


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


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "get_full_name",
        "role",
        "department",
        "hire_date",
        "is_active",
        "show_capabilities",
    )
    list_filter = (
        "role",
        "department",
        "is_active",
        "can_process_orders",
        "can_arrange_flowers",
        "can_deliver_orders",
        "can_manage_staff",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "department",
        "phone_extension",
    )
    readonly_fields = ("created_at", "updated_at")

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = "Name"

    def show_capabilities(self, obj):
        caps = []
        if obj.can_process_orders:
            caps.append("Process Orders")
        if obj.can_arrange_flowers:
            caps.append("Arrange Flowers")
        if obj.can_deliver_orders:
            caps.append("Deliver Orders")
        if obj.can_manage_staff:
            caps.append("Manage Staff")

        return ", ".join(caps) if caps else "None"

    show_capabilities.short_description = "Capabilities"

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Employee Details",
            {
                "fields": (
                    "role",
                    "department",
                    "hire_date",
                    "phone_extension",
                    "is_active",
                )
            },
        ),
        (
            "Capabilities",
            {
                "fields": (
                    "can_process_orders",
                    "can_arrange_flowers",
                    "can_deliver_orders",
                    "can_manage_staff",
                )
            },
        ),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(EmployeeOrderAssignment)
class EmployeeOrderAssignmentAdmin(admin.ModelAdmin):
    list_display = ("order", "employee", "role", "assigned_at")
    list_filter = ("role", "assigned_at")
    search_fields = (
        "order__reference_number",
        "employee__user__first_name",
        "employee__user__last_name",
        "notes",
    )
    date_hierarchy = "assigned_at"
