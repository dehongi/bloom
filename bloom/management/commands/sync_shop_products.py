from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from bloom.models import Product as BloomProduct
from shop.models import Product as ShopProduct, Category


class Command(BaseCommand):
    help = "Synchronizes bloom products to shop products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update of all products, even if they already have shop products",
        )

    def handle(self, *args, **options):
        force = options["force"]

        # Get all bloom products
        bloom_products = BloomProduct.objects.all()

        if not bloom_products.exists():
            self.stdout.write(self.style.WARNING("No bloom products found to sync"))
            return

        # Create default category if none exist
        if not Category.objects.exists():
            self.stdout.write(
                self.style.WARNING("No shop categories found. Creating a default one.")
            )
            Category.objects.create(
                name="Flowers",
                slug="flowers",
                description="Flower arrangements and bouquets",
            )

        # Track stats
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        # Process each bloom product
        for bloom_product in bloom_products:
            try:
                with transaction.atomic():
                    # Skip products that already have shop_product unless force is True
                    if bloom_product.shop_product and not force:
                        self.stdout.write(
                            f"Skipping {bloom_product.name} - already has shop product"
                        )
                        skipped_count += 1
                        continue

                    # Check if this is an update or create
                    if bloom_product.shop_product:
                        # Update existing shop product
                        shop_product = bloom_product.shop_product

                        # Update fields
                        shop_product.name = bloom_product.name
                        shop_product.description = (
                            bloom_product.description or shop_product.description
                        )
                        shop_product.price = bloom_product.price
                        shop_product.sku = bloom_product.sku

                        # Save changes
                        shop_product.save()

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated shop product for: {bloom_product.name}"
                            )
                        )
                        updated_count += 1
                    else:
                        # Try to find a default category for the product
                        default_category = None

                        # Check if a category with the same name as the product type exists
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

                        # Create a unique slug for the product
                        slug = slugify(bloom_product.name)
                        counter = 1
                        original_slug = slug

                        # Ensure slug is unique
                        while ShopProduct.objects.filter(slug=slug).exists():
                            slug = f"{original_slug}-{counter}"
                            counter += 1

                        # Create the shop product
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

                        # Update relationship (avoid triggering signals)
                        bloom_product._skip_shop_product_signal = True
                        bloom_product.shop_product = shop_product
                        bloom_product.save(update_fields=["shop_product"])

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created shop product for: {bloom_product.name}"
                            )
                        )
                        created_count += 1

            except Exception as e:
                errors.append(f"{bloom_product.name}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"Error processing {bloom_product.name}: {e}")
                )

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(f"Products processed: {len(bloom_products)}")
        )
        self.stdout.write(self.style.SUCCESS(f"Products created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Products updated: {updated_count}"))
        self.stdout.write(self.style.SUCCESS(f"Products skipped: {skipped_count}"))

        if errors:
            self.stdout.write(self.style.ERROR(f"Errors: {len(errors)}"))
            for error in errors:
                self.stdout.write(self.style.ERROR(f"  - {error}"))
        else:
            self.stdout.write(self.style.SUCCESS("Completed with no errors!"))
