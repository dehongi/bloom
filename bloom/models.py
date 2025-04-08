from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class Customer(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    external_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Occasion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)
    external_id = models.CharField(max_length=50, blank=True, null=True)
    occasions = models.ManyToManyField(Occasion, blank=True)

    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("design", "Design"),
        ("preparation", "Preparation"),
        ("delivery", "Delivery"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    reference_number = models.CharField(max_length=50, unique=True)
    salesorder_number = models.CharField(max_length=50, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField(default=timezone.now)
    shipment_date = models.DateField()
    delivery_method = models.ForeignKey(
        DeliveryMethod, on_delete=models.SET_NULL, null=True
    )
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Address information
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=50)
    shipping_state = models.CharField(max_length=50)
    shipping_country = models.CharField(max_length=50)
    shipping_postal_code = models.CharField(max_length=20)

    # Financial information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_type = models.CharField(max_length=20, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_discount_before_tax = models.BooleanField(default=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Order metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    notes = models.TextField(blank=True)
    occasion = models.ForeignKey(
        Occasion, on_delete=models.SET_NULL, null=True, blank=True
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-order_date"]

    def __str__(self):
        return self.reference_number

    def calculate_total(self):
        # Calculate order total
        self.subtotal = sum(item.get_total() for item in self.orderitem_set.all())

        # Apply discount
        if self.discount_percentage > 0:
            discount_amount = (self.subtotal * self.discount_percentage) / 100
            self.discount_value = discount_amount

        # Calculate total
        self.total = (
            self.subtotal - self.discount_value + self.shipping_charge + self.tax_amount
        )

        return self.total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    external_item_id = models.CharField(max_length=50, blank=True, null=True)
    header_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} - {self.order.reference_number}"

    def get_total(self):
        return self.price * self.quantity


class CustomField(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    field_id = models.CharField(max_length=50)
    value = models.TextField(blank=True)

    def __str__(self):
        return f"{self.field_id}: {self.value}"


class OrderStatus(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "Order Statuses"

    def __str__(self):
        return f"{self.order.reference_number} - {self.status}"
