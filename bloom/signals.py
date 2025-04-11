from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    Order as BloomOrder,
    OrderStatus,
    Product as BloomProduct,
    ProductType,
)
from shop.models import Product as ShopProduct, Category, Order as ShopOrder


@receiver(post_save, sender=OrderStatus)
def update_shop_order_on_status_change(sender, instance, created, **kwargs):
    """
    Signal handler to update the shop order when a new status is added to a bloom order.
    This ensures that status updates in the internal system reflect in the customer-facing system.
    """
    if created:  # Only handle newly created status entries
        bloom_order = instance.order

        # Skip if there's no shop order linked
        if (
            not hasattr(bloom_order, "shop_order_link")
            or not bloom_order.shop_order_link
        ):
            return

        # Map bloom status to shop status
        status_mapping = {
            "new": "pending",
            "design": "processing",
            "preparation": "processing",
            "delivery": "shipped",
            "completed": "delivered",
            "cancelled": "cancelled",
        }

        shop_order = bloom_order.shop_order_link
        bloom_status = instance.status
        shop_status = status_mapping.get(bloom_status)

        if shop_order.status != shop_status:
            shop_order._skip_bloom_signal = True  # Prevent signal loop
            shop_order.status = shop_status

            # If we're shipping, add a tracking number
            if bloom_status == "delivery" and shop_order.tracking_number == "":
                shop_order.tracking_number = f"BLM-{bloom_order.reference_number}"

            shop_order.save(update_fields=["status", "tracking_number"])


@receiver(post_save, sender=BloomProduct)
def create_or_update_shop_product(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a corresponding shop Product when a bloom Product is saved.
    This ensures products in the internal system are available in the customer-facing shop.
    """
    # Skip if this save was triggered by updating the shop_product field to avoid loops
    if (
        hasattr(instance, "_skip_shop_product_signal")
        and instance._skip_shop_product_signal
    ):
        return

    # If there's no shop product linked yet or we're creating a new product
    if not instance.shop_product:
        try:
            # Try to find a default category for the product
            # By product type or occasion if possible
            default_category = None
            try:
                # First check if the product type has a linked category
                if instance.product_type and hasattr(
                    instance.product_type, "shop_category"
                ):
                    default_category = instance.product_type.shop_category

                # If not, try to find a category with the same name as the product type
                elif instance.product_type:
                    default_category = Category.objects.filter(
                        name__iexact=instance.product_type.name
                    ).first()

                # If not found, try to match with an occasion
                if not default_category and instance.occasions.exists():
                    occasion_name = instance.occasions.first().name
                    default_category = Category.objects.filter(
                        name__iexact=occasion_name
                    ).first()

                # If still not found, use the first category
                if not default_category:
                    default_category = Category.objects.first()

            except (ObjectDoesNotExist, AttributeError):
                # If no categories exist, create a default one
                default_category, _ = Category.objects.get_or_create(
                    name="Flowers",
                    defaults={
                        "slug": "flowers",
                        "description": "Flower arrangements and bouquets",
                    },
                )

            # Create a unique slug for the product
            slug = slugify(instance.name)
            counter = 1
            original_slug = slug

            # Ensure slug is unique
            while ShopProduct.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            # Create the shop product
            shop_product = ShopProduct.objects.create(
                name=instance.name,
                slug=slug,
                sku=instance.sku,
                description=instance.description or f"Beautiful {instance.name}",
                price=instance.price,
                stock_quantity=10,  # Default initial stock
                is_active=True,
                in_stock=True,
                meta_title=instance.name,
                meta_description=f"Order {instance.name} from our flower shop",
            )

            # Add to default category
            if default_category:
                shop_product.categories.add(default_category)

            # Add secondary categories from occasions if they exist
            for occasion in instance.occasions.all():
                # Find or create a category for this occasion
                occasion_category, _ = Category.objects.get_or_create(
                    name=occasion.name,
                    defaults={
                        "slug": slugify(occasion.name),
                        "description": f"Products for {occasion.name}",
                    },
                )
                shop_product.categories.add(occasion_category)

            # Update relationship (avoid triggering signals again)
            instance._skip_shop_product_signal = True
            instance.shop_product = shop_product
            instance.save(update_fields=["shop_product"])

        except Exception as e:
            # Log the error for debugging
            print(f"Error creating shop product: {e}")
    else:
        # Update existing shop product
        shop_product = instance.shop_product

        # Update basic fields
        shop_product.name = instance.name
        shop_product.description = instance.description or shop_product.description
        shop_product.price = instance.price
        shop_product.sku = instance.sku

        # Update categories if needed
        # First, ensure it's in the primary category based on product_type
        if instance.product_type and hasattr(instance.product_type, "shop_category"):
            primary_category = instance.product_type.shop_category
            if (
                primary_category
                and primary_category not in shop_product.categories.all()
            ):
                shop_product.categories.add(primary_category)

        # Save changes
        shop_product.save()


@receiver(post_save, sender=ProductType)
def sync_product_type_to_category(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a corresponding Category when a ProductType is saved.
    This ensures internal product types are available as categories in the shop.
    """
    # Skip if this save was triggered by updating the Category to avoid loops
    if hasattr(instance, "_skip_category_signal") and instance._skip_category_signal:
        return

    try:
        # If there's already a category linked
        if hasattr(instance, "shop_category") and instance.shop_category:
            # Update the existing category if the name changed
            if instance.shop_category.name != instance.name:
                instance.shop_category._skip_product_type_signal = True
                instance.shop_category.name = instance.name
                instance.shop_category.save(update_fields=["name"])
        else:
            # Create a new category for this product type
            # Generate a unique slug
            slug = slugify(instance.name)
            counter = 1
            original_slug = slug

            # Ensure slug is unique
            while Category.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            # Create category with product_type reference
            category = Category.objects.create(
                name=instance.name,
                slug=slug,
                description=f"Products in the {instance.name} category",
                product_type=instance,
                featured=False,  # Default to not featured
                order=Category.objects.count() + 1,  # Add at the end
            )
    except Exception as e:
        # Log any errors
        print(f"Error syncing ProductType to Category: {e}")
