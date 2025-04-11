from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from .models import Order as ShopOrder, Product as ShopProduct, Category
from bloom.models import (
    Order as BloomOrder,
    Customer,
    DeliveryMethod,
    OrderStatus,
    Product as BloomProduct,
    ProductType,
)


@receiver(post_save, sender=ShopOrder)
def create_or_update_bloom_order(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a corresponding bloom Order when a shop Order is saved.
    This connects the customer-facing ordering system with the internal management system.
    """
    # Skip if this save was triggered by updating the bloom_order field to avoid loops
    if hasattr(instance, "_skip_bloom_signal") and instance._skip_bloom_signal:
        return

    # Map shop status to bloom status
    status_mapping = {
        "pending": "new",
        "processing": "design",
        "shipped": "delivery",
        "delivered": "completed",
        "cancelled": "cancelled",
    }

    # If there's no bloom order linked yet or we're creating a new order
    if not instance.bloom_order:
        try:
            # Get or create a bloom customer record
            customer, _ = Customer.objects.get_or_create(
                email=instance.email,
                defaults={
                    "name": instance.full_name,
                    "phone": instance.phone,
                    "address": f"{instance.address_line_1}\n{instance.address_line_2 or ''}",
                    "city": instance.city,
                    "state": instance.state,
                    "country": instance.country,
                    "postal_code": instance.postal_code,
                    "user": instance.user,
                },
            )

            # Get default delivery method or create one if none exists
            try:
                delivery_method = DeliveryMethod.objects.first()
                if not delivery_method:
                    delivery_method = DeliveryMethod.objects.create(
                        name="Standard Delivery",
                        description="Standard delivery option",
                        price=0.00,
                    )
            except Exception as e:
                # If there's an error, log it and create a basic delivery method
                print(f"Error getting delivery method: {e}")
                delivery_method = DeliveryMethod.objects.create(
                    name="Standard Delivery",
                    description="Standard delivery option",
                    price=0.00,
                )

            # Create bloom order
            bloom_order = BloomOrder.objects.create(
                reference_number=f"SHOP-{instance.order_number}",
                salesorder_number=instance.order_number,
                customer=customer,
                order_date=instance.created_at.date(),
                shipment_date=timezone.now().date()
                + timezone.timedelta(days=3),  # Default to 3 days for shipping
                delivery_method=delivery_method,
                shipping_charge=instance.shipping_cost,
                recipient_name=instance.full_name,
                recipient_phone=instance.phone,
                shipping_address=f"{instance.address_line_1}\n{instance.address_line_2 or ''}",
                shipping_city=instance.city,
                shipping_state=instance.state,
                shipping_country=instance.country,
                shipping_postal_code=instance.postal_code,
                subtotal=instance.subtotal,
                discount_value=instance.discount_amount,
                tax_amount=instance.tax_amount,
                total=instance.total,
                status=status_mapping.get(instance.status, "new"),
                notes=instance.order_notes or "",
            )

            # Create bloom order items
            for item in instance.items.all():
                product = None
                # Try to find matching bloom product by product's bloom_product_link relationship
                if item.product and hasattr(item.product, "bloom_product_link"):
                    product = item.product.bloom_product_link

                bloom_order.orderitem_set.create(
                    product=product,  # May be None if no matching product
                    name=item.product_name,
                    description=f"{item.variant_name or ''}",
                    price=item.price,
                    quantity=item.quantity,
                    external_item_id=str(item.id),
                )

            # Create initial order status
            OrderStatus.objects.create(
                order=bloom_order,
                status=bloom_order.status,
                notes="Order created from online shop",
                updated_by=None,
            )

            # Update relationship (avoid triggering signals again)
            instance._skip_bloom_signal = True
            instance.bloom_order = bloom_order
            instance.save(update_fields=["bloom_order"])

            # Set shop_order_link on bloom_order
            bloom_order.shop_order_link = instance
            bloom_order.save(update_fields=["shop_order_link"])

        except Exception as e:
            # Log the error for debugging
            print(f"Error creating bloom order: {e}")
    else:
        # Update existing bloom order if status changed
        bloom_order = instance.bloom_order
        shop_status = instance.status
        bloom_status = status_mapping.get(shop_status)

        if bloom_order.status != bloom_status:
            old_status = bloom_order.status
            bloom_order.status = bloom_status
            bloom_order.save(update_fields=["status"])

            # Add status history entry
            OrderStatus.objects.create(
                order=bloom_order,
                status=bloom_status,
                notes=f"Status updated from online shop (was: {old_status})",
                updated_by=None,
            )


@receiver(post_save, sender=BloomOrder)
def update_shop_order_from_bloom(sender, instance, **kwargs):
    """
    Signal handler to update a shop Order when a bloom Order is updated.
    This ensures changes in the internal system reflect back to the customer-facing system.
    """
    # Skip if this save was triggered by updating the shop_order field to avoid loops
    if hasattr(instance, "_skip_shop_signal") and instance._skip_shop_signal:
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

    # If there's a shop order linked
    if hasattr(instance, "shop_order_link") and instance.shop_order_link:
        shop_order = instance.shop_order_link

        # Update shop order status if it has changed
        bloom_status = instance.status
        shop_status = status_mapping.get(bloom_status)

        if shop_order.status != shop_status:
            shop_order._skip_bloom_signal = True  # Prevent signal loop
            shop_order.status = shop_status

            # Add tracking number if available and we're shipping
            if bloom_status == "delivery" and shop_order.tracking_number == "":
                shop_order.tracking_number = f"BLM-{instance.reference_number}"

            shop_order.save(update_fields=["status", "tracking_number"])


@receiver(post_save, sender=ShopProduct)
def update_bloom_product_from_shop(sender, instance, **kwargs):
    """
    Signal handler to update bloom product when shop product is updated.
    This keeps product information consistent between the systems.
    """
    # Skip if this save was triggered by updating the bloom_product_link to avoid loops
    if (
        hasattr(instance, "_skip_bloom_product_signal")
        and instance._skip_bloom_product_signal
    ):
        return

    # If there's a bloom product linked
    if hasattr(instance, "bloom_product_link") and instance.bloom_product_link:
        bloom_product = instance.bloom_product_link

        # Only update price (description is managed by bloom)
        if bloom_product.price != instance.price:
            bloom_product._skip_shop_product_signal = True
            bloom_product.price = instance.price
            bloom_product.save(update_fields=["price"])

        # Note: we're not syncing stock quantities here since bloom doesn't track them


@receiver(post_save, sender=BloomProduct)
def update_shop_product_from_bloom(sender, instance, **kwargs):
    """
    Signal handler to update shop product when bloom product is updated.
    This keeps product information consistent between the systems.
    """
    # Skip if this save was triggered by updating from shop product to avoid loops
    if (
        hasattr(instance, "_skip_shop_product_signal")
        and instance._skip_shop_product_signal
    ):
        return

    # If there's a shop product linked
    if instance.shop_product:
        shop_product = instance.shop_product

        # Update basic fields that bloom manages
        shop_product._skip_bloom_product_signal = True
        shop_product.name = instance.name
        shop_product.sku = instance.sku
        shop_product.price = instance.price
        shop_product.description = instance.description or shop_product.description

        # Save changes
        shop_product.save(update_fields=["name", "sku", "price", "description"])


@receiver(post_save, sender=Category)
def sync_category_to_product_type(sender, instance, created, **kwargs):
    """
    Signal handler to create or update a corresponding ProductType when a Category is saved.
    This ensures that shop categories are available as product types in the internal system.
    """
    # Skip if this save was triggered by updating from ProductType to avoid loops
    if (
        hasattr(instance, "_skip_product_type_signal")
        and instance._skip_product_type_signal
    ):
        return

    # Only sync top-level categories (parent=None) to ProductType
    if instance.parent is not None:
        return

    try:
        # If there's a product_type linked
        if instance.product_type:
            # Update the product type if the name has changed
            if instance.product_type.name != instance.name:
                instance.product_type._skip_category_signal = True
                instance.product_type.name = instance.name
                instance.product_type.save()
        else:
            # Create a new ProductType for this category
            product_type = ProductType.objects.create(name=instance.name)

            # Link back to the category without triggering the sync again
            instance._skip_product_type_signal = True
            instance.product_type = product_type
            instance.save(update_fields=["product_type"])
    except Exception as e:
        # Log any errors
        print(f"Error syncing Category to ProductType: {e}")
