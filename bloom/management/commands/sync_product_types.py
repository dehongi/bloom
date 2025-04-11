from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from bloom.models import ProductType
from shop.models import Category


class Command(BaseCommand):
    help = "Synchronizes ProductTypes to Categories in the shop"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update of all categories, even if they already exist",
        )
        parser.add_argument(
            "--bidirectional",
            action="store_true",
            help="Also sync Categories to ProductTypes",
        )

    def handle(self, *args, **options):
        force = options["force"]
        bidirectional = options["bidirectional"]

        # Sync ProductTypes to Categories
        self.sync_product_types_to_categories(force)

        # If bidirectional is enabled, also sync Categories to ProductTypes
        if bidirectional:
            self.sync_categories_to_product_types(force)

        self.stdout.write(self.style.SUCCESS("Synchronization complete!"))

    def sync_product_types_to_categories(self, force):
        """Sync all ProductTypes to Categories"""
        product_types = ProductType.objects.all()

        if not product_types.exists():
            self.stdout.write(self.style.WARNING("No product types found to sync"))
            return

        self.stdout.write(
            f"Syncing {product_types.count()} product types to categories..."
        )

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for product_type in product_types:
            try:
                with transaction.atomic():
                    # Skip if already has a category and force is False
                    if (
                        hasattr(product_type, "shop_category")
                        and product_type.shop_category
                        and not force
                    ):
                        skipped_count += 1
                        continue

                    # Check if this is an update or create
                    if (
                        hasattr(product_type, "shop_category")
                        and product_type.shop_category
                    ):
                        # Update existing category
                        category = product_type.shop_category

                        # Skip if name is the same
                        if category.name == product_type.name:
                            skipped_count += 1
                            continue

                        # Update name
                        category._skip_product_type_signal = True
                        category.name = product_type.name
                        category.save(update_fields=["name"])

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated category for: {product_type.name}"
                            )
                        )
                        updated_count += 1
                    else:
                        # Create a new category
                        # Create a unique slug
                        slug = slugify(product_type.name)
                        counter = 1
                        original_slug = slug

                        # Ensure slug is unique
                        while Category.objects.filter(slug=slug).exists():
                            slug = f"{original_slug}-{counter}"
                            counter += 1

                        # Create the category
                        category = Category.objects.create(
                            name=product_type.name,
                            slug=slug,
                            description=f"Products in the {product_type.name} category",
                            product_type=product_type,
                            featured=False,
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created category for: {product_type.name}"
                            )
                        )
                        created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {product_type.name}: {e}")
                )

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(f"ProductTypes processed: {product_types.count()}")
        )
        self.stdout.write(self.style.SUCCESS(f"Categories created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Categories updated: {updated_count}"))
        self.stdout.write(self.style.SUCCESS(f"ProductTypes skipped: {skipped_count}"))

    def sync_categories_to_product_types(self, force):
        """Sync top-level Categories to ProductTypes"""
        categories = Category.objects.filter(parent=None)

        if not categories.exists():
            self.stdout.write(
                self.style.WARNING("No top-level categories found to sync")
            )
            return

        self.stdout.write(
            f"Syncing {categories.count()} top-level categories to product types..."
        )

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for category in categories:
            try:
                with transaction.atomic():
                    # Skip if already has a product_type and force is False
                    if category.product_type and not force:
                        skipped_count += 1
                        continue

                    # Check if this is an update or create
                    if category.product_type:
                        # Update existing product type
                        product_type = category.product_type

                        # Skip if name is the same
                        if product_type.name == category.name:
                            skipped_count += 1
                            continue

                        # Update name
                        product_type._skip_category_signal = True
                        product_type.name = category.name
                        product_type.save()

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated product type for: {category.name}"
                            )
                        )
                        updated_count += 1
                    else:
                        # Create a new product type
                        product_type = ProductType.objects.create(name=category.name)

                        # Link back to category
                        category._skip_product_type_signal = True
                        category.product_type = product_type
                        category.save(update_fields=["product_type"])

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created product type for: {category.name}"
                            )
                        )
                        created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {category.name}: {e}")
                )

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(f"Categories processed: {categories.count()}")
        )
        self.stdout.write(self.style.SUCCESS(f"ProductTypes created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"ProductTypes updated: {updated_count}"))
        self.stdout.write(self.style.SUCCESS(f"Categories skipped: {skipped_count}"))
