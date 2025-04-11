from django import forms
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
    ContactPerson,
)
from accounts.models import CustomUser


class BootstrapModelForm(forms.ModelForm):
    """Base model form with Bootstrap 5 styling for all form fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = "form-control"
            if isinstance(field, forms.BooleanField):
                css_class = "form-check-input"
            elif isinstance(field, forms.DateField) or isinstance(
                field, forms.DateTimeField
            ):
                css_class = "form-control datepicker"

            field.widget.attrs.update(
                {
                    "class": css_class,
                    "placeholder": field.label
                    or field_name.replace("_", " ").capitalize(),
                }
            )


class CustomerForm(BootstrapModelForm):
    class Meta:
        model = Customer
        fields = [
            "name",
            "company_name",
            "contact_type",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "notes",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class OccasionForm(BootstrapModelForm):
    class Meta:
        model = Occasion
        fields = ["name"]


class ProductTypeForm(BootstrapModelForm):
    class Meta:
        model = ProductType
        fields = ["name"]


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "description", "price", "product_type", "occasions"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "occasions": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the default class for checkboxes
        if "occasions" in self.fields:
            self.fields["occasions"].widget.attrs.pop("class", None)


class DeliveryMethodForm(BootstrapModelForm):
    class Meta:
        model = DeliveryMethod
        fields = ["name", "description", "price"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class OrderForm(BootstrapModelForm):
    class Meta:
        model = Order
        fields = [
            "reference_number",
            "salesorder_number",
            "customer",
            "order_date",
            "shipment_date",
            "delivery_method",
            "shipping_charge",
            "recipient_name",
            "recipient_phone",
            "shipping_address",
            "shipping_city",
            "shipping_state",
            "shipping_country",
            "shipping_postal_code",
            "discount_type",
            "discount_percentage",
            "is_discount_before_tax",
            "notes",
            "occasion",
            "message",
            "status",
        ]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "shipment_date": forms.DateInput(attrs={"type": "date"}),
            "shipping_address": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "message": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        shipment_date = cleaned_data.get("shipment_date")
        order_date = cleaned_data.get("order_date")

        if shipment_date and order_date and shipment_date < order_date:
            self.add_error(
                "shipment_date", "Shipment date cannot be before order date."
            )

        return cleaned_data


class OrderItemForm(BootstrapModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "name", "description", "price", "quantity", "header_name"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate name and price when product is selected
        if "product" in self.fields:
            self.fields["product"].widget.attrs.update(
                {
                    "data-product-select": "true",
                }
            )


class OrderItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Check for at least one item in the order
        if any(self.errors):
            return
        if not any(
            form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            for form in self.forms
        ):
            raise forms.ValidationError("At least one item is required in the order.")


class CustomFieldForm(BootstrapModelForm):
    class Meta:
        model = CustomField
        fields = ["field_id", "value"]
        widgets = {
            "value": forms.Textarea(attrs={"rows": 2}),
        }


class OrderStatusForm(BootstrapModelForm):
    class Meta:
        model = OrderStatus
        fields = ["status", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].required = False


# Search and Filter Forms
class OrderSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search orders..."}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Statuses")] + Order.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date", "placeholder": "From Date"}
        ),
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date", "placeholder": "To Date"}
        ),
    )


class ProductSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search products..."}
        ),
    )
    product_type = forms.ModelChoiceField(
        required=False,
        queryset=ProductType.objects.all(),
        empty_label="All Types",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    occasion = forms.ModelChoiceField(
        required=False,
        queryset=Occasion.objects.all(),
        empty_label="All Occasions",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class EmployeeForm(BootstrapModelForm):
    # Explicitly define the user field
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        required=True,
        label="User",
        empty_label="Select User",
    )

    class Meta:
        model = Employee
        fields = [
            "user",
            "role",
            "department",
            "hire_date",
            "phone_extension",
            "is_active",
            "can_process_orders",
            "can_arrange_flowers",
            "can_deliver_orders",
            "can_manage_staff",
        ]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter out users who are already employees
        if self.instance and self.instance.pk:
            # Editing an existing employee - include their current user in queryset
            existing_employee_users = Employee.objects.exclude(
                pk=self.instance.pk
            ).values_list("user_id", flat=True)
        else:
            # Creating a new employee - exclude all existing employee users
            existing_employee_users = Employee.objects.values_list("user_id", flat=True)

        # Filter users, only showing active users who aren't already employees (except current user when editing)
        self.fields["user"].queryset = CustomUser.objects.filter(
            is_active=True
        ).exclude(id__in=existing_employee_users)

        # If there are no available users, add a helpful message
        if not self.fields["user"].queryset.exists() and not self.instance.pk:
            self.fields["user"].empty_label = "No available users - create a new one"

    def clean(self):
        cleaned_data = super().clean()

        # Check if we're creating a new user - if so, make the user field optional
        if self.data.get("create_new_user") == "true":
            # Remove the error for the user field if it exists
            if "user" in self.errors:
                del self.errors["user"]
            # Make user field not required
            self.fields["user"].required = False

        return cleaned_data


class EmployeeSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search employees..."}
        ),
    )
    role = forms.ChoiceField(
        required=False,
        choices=[("", "All Roles")] + Employee.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Department"}
        ),
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            attrs={"class": "form-select"},
            choices=[
                ("", "All Employees"),
                (True, "Active Employees"),
                (False, "Inactive Employees"),
            ],
        ),
    )


class EmployeeOrderAssignmentForm(BootstrapModelForm):
    class Meta:
        model = EmployeeOrderAssignment
        fields = ["employee", "role", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter employees by capabilities based on role
        self.fields["employee"].queryset = Employee.objects.filter(is_active=True)

        # Set up role-based filtering dynamically via JavaScript
        self.fields["role"].widget.attrs.update(
            {
                "class": "form-select role-selector",
                "data-designer-filter": "can_arrange_flowers",
                "data-delivery-filter": "can_deliver_orders",
                "data-processor-filter": "can_process_orders",
                "data-manager-filter": "can_manage_staff",
            }
        )
    )


class ContactPersonForm(BootstrapModelForm):
    class Meta:
        model = ContactPerson
        fields = [
            "salutation",
            "first_name",
            "last_name",
            "email",
            "phone",
            "mobile",
            "is_primary_contact",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_primary_contact"].widget.attrs.update(
            {"class": "form-check-input ms-0"}
        )
        self.fields["salutation"].required = False
