from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
    TemplateView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.forms import inlineformset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone

from .models import (
    Customer,
    ContactPerson,
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
from .forms import (
    CustomerForm,
    ContactPersonForm,
    OccasionForm,
    ProductTypeForm,
    ProductForm,
    DeliveryMethodForm,
    OrderForm,
    OrderItemForm,
    CustomFieldForm,
    OrderStatusForm,
    OrderSearchForm,
    ProductSearchForm,
    OrderItemFormSet,
    EmployeeForm,
    EmployeeSearchForm,
    EmployeeOrderAssignmentForm,
)


# Mixins
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff access for views"""

    def test_func(self):
        return self.request.user.is_staff


# Customer Views
class CustomerListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Customer
    template_name = "bloom/customer_list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get("search", "")

        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term)
                | Q(email__icontains=search_term)
                | Q(phone__icontains=search_term)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_term"] = self.request.GET.get("search", "")
        return context


class CustomerDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Customer
    template_name = "bloom/customer_detail.html"
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders"] = Order.objects.filter(customer=self.object).order_by(
            "-order_date"
        )
        return context


class CustomerCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "bloom/customer_form.html"
    success_url = reverse_lazy("bloom:customer_list")

    def form_valid(self, form):
        messages.success(self.request, "Customer created successfully.")
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "bloom/customer_form.html"

    def get_success_url(self):
        return reverse_lazy("bloom:customer_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Customer updated successfully.")
        return super().form_valid(form)


class CustomerDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Customer
    template_name = "bloom/customer_confirm_delete.html"
    success_url = reverse_lazy("bloom:customer_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Customer deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ContactPerson Views
class ContactPersonCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ContactPerson
    form_class = ContactPersonForm
    template_name = "bloom/contact_person_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = get_object_or_404(Customer, pk=self.kwargs["customer_pk"])
        return context

    def form_valid(self, form):
        form.instance.customer = get_object_or_404(
            Customer, pk=self.kwargs["customer_pk"]
        )
        messages.success(self.request, "Contact person added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "bloom:customer_detail", kwargs={"pk": self.kwargs["customer_pk"]}
        )


class ContactPersonUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ContactPerson
    form_class = ContactPersonForm
    template_name = "bloom/contact_person_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "bloom:customer_detail", kwargs={"pk": self.object.customer.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "Contact person updated successfully.")
        return super().form_valid(form)


class ContactPersonDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ContactPerson
    template_name = "bloom/contact_person_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "bloom:customer_detail", kwargs={"pk": self.object.customer.pk}
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Contact person deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Occasion Views
class OccasionListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Occasion
    template_name = "bloom/occasion_list.html"
    context_object_name = "occasions"


class OccasionCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Occasion
    form_class = OccasionForm
    template_name = "bloom/occasion_form.html"
    success_url = reverse_lazy("bloom:occasion_list")

    def form_valid(self, form):
        messages.success(self.request, "Occasion created successfully.")
        return super().form_valid(form)


class OccasionUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Occasion
    form_class = OccasionForm
    template_name = "bloom/occasion_form.html"
    success_url = reverse_lazy("bloom:occasion_list")

    def form_valid(self, form):
        messages.success(self.request, "Occasion updated successfully.")
        return super().form_valid(form)


class OccasionDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Occasion
    template_name = "bloom/occasion_confirm_delete.html"
    success_url = reverse_lazy("bloom:occasion_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Occasion deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ProductType Views
class ProductTypeListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ProductType
    template_name = "bloom/product_type_list.html"
    context_object_name = "product_types"


class ProductTypeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = "bloom/product_type_form.html"
    success_url = reverse_lazy("bloom:product_type_list")

    def form_valid(self, form):
        messages.success(self.request, "Product Type created successfully.")
        return super().form_valid(form)


class ProductTypeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = "bloom/product_type_form.html"
    success_url = reverse_lazy("bloom:product_type_list")

    def form_valid(self, form):
        messages.success(self.request, "Product Type updated successfully.")
        return super().form_valid(form)


class ProductTypeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ProductType
    template_name = "bloom/product_type_confirm_delete.html"
    success_url = reverse_lazy("bloom:product_type_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Product Type deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "bloom/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ProductSearchForm(self.request.GET)

        if form.is_valid():
            search = form.cleaned_data.get("search")
            product_type = form.cleaned_data.get("product_type")
            occasion = form.cleaned_data.get("occasion")

            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search)
                    | Q(sku__icontains=search)
                    | Q(description__icontains=search)
                )

            if product_type:
                queryset = queryset.filter(product_type=product_type)

            if occasion:
                queryset = queryset.filter(occasions=occasion)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ProductSearchForm(self.request.GET)
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "bloom/product_detail.html"
    context_object_name = "product"


class ProductCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "bloom/product_form.html"
    success_url = reverse_lazy("bloom:product_list")

    def form_valid(self, form):
        messages.success(self.request, "Product created successfully.")
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "bloom/product_form.html"

    def get_success_url(self):
        return reverse_lazy("bloom:product_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully.")
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Product
    template_name = "bloom/product_confirm_delete.html"
    success_url = reverse_lazy("bloom:product_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Product deleted successfully.")
        return super().delete(request, *args, **kwargs)


# DeliveryMethod Views
class DeliveryMethodListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = DeliveryMethod
    template_name = "bloom/delivery_method_list.html"
    context_object_name = "delivery_methods"


class DeliveryMethodCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = DeliveryMethod
    form_class = DeliveryMethodForm
    template_name = "bloom/delivery_method_form.html"
    success_url = reverse_lazy("bloom:delivery_method_list")

    def form_valid(self, form):
        messages.success(self.request, "Delivery Method created successfully.")
        return super().form_valid(form)


class DeliveryMethodUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = DeliveryMethod
    form_class = DeliveryMethodForm
    template_name = "bloom/delivery_method_form.html"
    success_url = reverse_lazy("bloom:delivery_method_list")

    def form_valid(self, form):
        messages.success(self.request, "Delivery Method updated successfully.")
        return super().form_valid(form)


class DeliveryMethodDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = DeliveryMethod
    template_name = "bloom/delivery_method_confirm_delete.html"
    success_url = reverse_lazy("bloom:delivery_method_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Delivery Method deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Order Views
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "bloom/order_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        form = OrderSearchForm(self.request.GET)

        if form.is_valid():
            search = form.cleaned_data.get("search")
            status = form.cleaned_data.get("status")
            from_date = form.cleaned_data.get("from_date")
            to_date = form.cleaned_data.get("to_date")

            if search:
                queryset = queryset.filter(
                    Q(reference_number__icontains=search)
                    | Q(salesorder_number__icontains=search)
                    | Q(customer__name__icontains=search)
                    | Q(shipping_address__icontains=search)
                )

            if status:
                queryset = queryset.filter(status=status)

            if from_date:
                queryset = queryset.filter(order_date__gte=from_date)

            if to_date:
                queryset = queryset.filter(order_date__lte=to_date)

        return queryset.order_by("-order_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = OrderSearchForm(self.request.GET)
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "bloom/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = OrderItem.objects.filter(order=self.object)
        context["custom_fields"] = CustomField.objects.filter(order=self.object)
        context["status_history"] = OrderStatus.objects.filter(order=self.object)
        context["status_form"] = OrderStatusForm(initial={"status": self.object.status})

        # Add employee information to context
        context["designers"] = Employee.objects.filter(can_arrange_flowers=True)
        context["delivery_staff"] = Employee.objects.filter(can_deliver_orders=True)
        context["processors"] = Employee.objects.filter(can_process_orders=True)

        # Get assignment history for this order
        context["employee_assignments"] = EmployeeOrderAssignment.objects.filter(
            order=self.object
        ).select_related("employee", "assigned_by")

        return context


class OrderCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "bloom/order_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = inlineformset_factory(
                Order,
                OrderItem,
                form=OrderItemForm,
                formset=OrderItemFormSet,
                extra=1,
                can_delete=True,
            )(self.request.POST)
        else:
            context["items_formset"] = inlineformset_factory(
                Order,
                OrderItem,
                form=OrderItemForm,
                formset=OrderItemFormSet,
                extra=1,
                can_delete=True,
            )()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context["items_formset"]

        if items_formset.is_valid():
            self.object = form.save()

            # Save order items
            items_formset.instance = self.object
            items_formset.save()

            # Create initial status
            OrderStatus.objects.create(
                order=self.object,
                status=self.object.status,
                updated_by=self.request.user,
                notes="Order created",
            )

            # Calculate and save total
            self.object.calculate_total()
            self.object.save()

            messages.success(self.request, "Order created successfully.")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("bloom:order_detail", kwargs={"pk": self.object.pk})


class OrderUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "bloom/order_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = inlineformset_factory(
                Order,
                OrderItem,
                form=OrderItemForm,
                formset=OrderItemFormSet,
                extra=1,
                can_delete=True,
            )(self.request.POST, instance=self.object)
        else:
            context["items_formset"] = inlineformset_factory(
                Order,
                OrderItem,
                form=OrderItemForm,
                formset=OrderItemFormSet,
                extra=1,
                can_delete=True,
            )(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context["items_formset"]

        if items_formset.is_valid():
            # Save the order
            old_status = self.object.status
            self.object = form.save()

            # Save order items
            items_formset.instance = self.object
            items_formset.save()

            # Create status update if status changed
            if old_status != self.object.status:
                OrderStatus.objects.create(
                    order=self.object,
                    status=self.object.status,
                    updated_by=self.request.user,
                    notes=f"Status changed from {old_status} to {self.object.status}",
                )

            # Calculate and save total
            self.object.calculate_total()
            self.object.save()

            messages.success(self.request, "Order updated successfully.")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("bloom:order_detail", kwargs={"pk": self.object.pk})


class OrderDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Order
    template_name = "bloom/order_confirm_delete.html"
    success_url = reverse_lazy("bloom:order_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Order deleted successfully.")
        return super().delete(request, *args, **kwargs)


class UpdateOrderStatusView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = OrderStatusForm(request.POST)

        if form.is_valid():
            new_status = form.cleaned_data["status"]
            notes = form.cleaned_data.get("notes", "")

            # Update order status
            old_status = order.status
            order.status = new_status
            order.save()

            # Get the employee record of the current user if available
            employee = None
            try:
                employee = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                pass

            # Create status history entry with employee if available
            status_update = OrderStatus.objects.create(
                order=order,
                status=new_status,
                notes=notes,
                updated_by=request.user,
                updated_by_employee=employee,
            )

            messages.success(
                request, f"Order status updated from {old_status} to {new_status}"
            )
        else:
            messages.error(request, "Error updating order status.")

        return redirect("bloom:order_detail", pk=pk)


# Dashboard Views
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "bloom/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get orders by status for the pie chart
        status_counts = (
            Order.objects.values("status").annotate(count=Sum("id")).order_by()
        )

        # Get recent orders
        recent_orders = Order.objects.order_by("-created_at")[:10]

        # Get recent status updates with employee information
        recent_status_updates = OrderStatus.objects.select_related(
            "updated_by_employee", "order"
        ).order_by("-timestamp")[:10]

        # Get top employees by status updates in the last 30 days
        today = timezone.now().date()
        thirty_days_ago = today - timezone.timedelta(days=30)

        top_status_updaters = (
            OrderStatus.objects.filter(
                timestamp__date__gte=thirty_days_ago, updated_by_employee__isnull=False
            )
            .values(
                "updated_by_employee__user__first_name",
                "updated_by_employee__user__last_name",
            )
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        # Statistical data
        context.update(
            {
                "total_orders": Order.objects.count(),
                "pending_orders": Order.objects.filter(
                    status__in=["new", "design", "preparation"]
                ).count(),
                "delivery_orders": Order.objects.filter(status="delivery").count(),
                "completed_orders": Order.objects.filter(status="completed").count(),
                "recent_orders": recent_orders,
                "status_counts": status_counts,
                "today": today,
                "thirty_days_ago": thirty_days_ago,
                "recent_status_updates": recent_status_updates,
                "top_status_updaters": top_status_updaters,
            }
        )

        return context


# AJAX Views for Dynamic Forms
class GetProductInfoView(LoginRequiredMixin, View):
    def get(self, request):
        product_id = request.GET.get("product_id")
        try:
            product = Product.objects.get(pk=product_id)
            return JsonResponse(
                {
                    "name": product.name,
                    "price": str(product.price),
                    "description": product.description,
                    "sku": product.sku,
                }
            )
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)


# Custom Field Views
class CustomFieldCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = CustomField
    form_class = CustomFieldForm
    template_name = "bloom/custom_field_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "bloom:order_detail", kwargs={"pk": self.kwargs["order_pk"]}
        )

    def form_valid(self, form):
        form.instance.order_id = self.kwargs["order_pk"]
        messages.success(self.request, "Custom field added successfully.")
        return super().form_valid(form)


class CustomFieldUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = CustomField
    form_class = CustomFieldForm
    template_name = "bloom/custom_field_form.html"

    def get_success_url(self):
        return reverse_lazy("bloom:order_detail", kwargs={"pk": self.object.order.pk})

    def form_valid(self, form):
        messages.success(self.request, "Custom field updated successfully.")
        return super().form_valid(form)


class CustomFieldDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = CustomField
    template_name = "bloom/custom_field_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("bloom:order_detail", kwargs={"pk": self.object.order.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Custom field deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Employee Views
class EmployeeListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Employee
    template_name = "bloom/employee_list.html"
    context_object_name = "employees"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        form = EmployeeSearchForm(self.request.GET)

        if form.is_valid():
            search = form.cleaned_data.get("search")
            role = form.cleaned_data.get("role")
            department = form.cleaned_data.get("department")
            is_active = form.cleaned_data.get("is_active")

            if search:
                queryset = queryset.filter(
                    Q(user__first_name__icontains=search)
                    | Q(user__last_name__icontains=search)
                    | Q(user__email__icontains=search)
                    | Q(department__icontains=search)
                    | Q(phone_extension__icontains=search)
                )

            if role:
                queryset = queryset.filter(role=role)

            if department:
                queryset = queryset.filter(department__icontains=department)

            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = EmployeeSearchForm(self.request.GET)
        return context


class EmployeeDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Employee
    template_name = "bloom/employee_detail.html"
    context_object_name = "employee"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object

        # Get orders associated with this employee
        context["designed_orders"] = Order.objects.filter(assigned_designer=employee)
        context["delivered_orders"] = Order.objects.filter(assigned_delivery=employee)
        context["processed_orders"] = Order.objects.filter(processed_by=employee)

        # Get assignment history
        context["assignments"] = EmployeeOrderAssignment.objects.filter(
            employee=employee
        ).select_related("order")

        # Get active assignments
        context["active_assignments"] = EmployeeOrderAssignment.objects.filter(
            employee=employee, completed=False
        ).select_related("order")

        return context


class EmployeeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "bloom/employee_form.html"
    success_url = reverse_lazy("bloom:employee_list")

    def form_valid(self, form):
        # Check if this is a request to create a new user along with the employee
        if (
            self.request.user.is_superuser
            and self.request.POST.get("create_new_user") == "true"
        ):
            # Create a new user
            from accounts.models import CustomUser
            from django.contrib.auth.hashers import make_password

            try:
                email = self.request.POST.get("new_email")
                first_name = self.request.POST.get("new_first_name")
                last_name = self.request.POST.get("new_last_name")
                password = self.request.POST.get("new_password1")
                is_staff = self.request.POST.get("new_is_staff") == "on"

                # Validate that passwords match
                if password != self.request.POST.get("new_password2"):
                    messages.error(self.request, "Passwords don't match.")
                    return self.form_invalid(form)

                # Check if user with this email already exists
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(
                        self.request, f"A user with email {email} already exists."
                    )
                    return self.form_invalid(form)

                # Create the user
                user = CustomUser.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=is_staff,
                    password=make_password(password),
                )

                # Set the user in the form
                form.instance.user = user
                messages.success(
                    self.request,
                    f"New user {user.get_full_name()} created successfully.",
                )

            except Exception as e:
                messages.error(self.request, f"Error creating new user: {str(e)}")
                return self.form_invalid(form)

        messages.success(self.request, "Employee created successfully.")
        return super().form_valid(form)


class EmployeeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "bloom/employee_form.html"

    def get_success_url(self):
        return reverse_lazy("bloom:employee_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Employee updated successfully.")
        return super().form_valid(form)


class EmployeeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Employee
    template_name = "bloom/employee_confirm_delete.html"
    success_url = reverse_lazy("bloom:employee_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Employee record deleted successfully.")
        return super().delete(request, *args, **kwargs)


class AssignEmployeeToOrderView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = EmployeeOrderAssignment
    form_class = EmployeeOrderAssignmentForm
    template_name = "bloom/employee_order_assignment_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = get_object_or_404(Order, pk=self.kwargs["order_pk"])
        return context

    def form_valid(self, form):
        # Set the order
        form.instance.order_id = self.kwargs["order_pk"]

        # Set the assigner to current user's employee record if it exists
        try:
            form.instance.assigned_by = Employee.objects.get(user=self.request.user)
        except Employee.DoesNotExist:
            pass

        # Save the assignment
        response = super().form_valid(form)

        # Update the order with the assigned employee based on role
        order = self.object.order
        employee = self.object.employee
        role = self.object.role

        if role == "designer" and employee.can_arrange_flowers:
            order.assigned_designer = employee
        elif role == "delivery" and employee.can_deliver_orders:
            order.assigned_delivery = employee
        elif role in ["manager", "sales"] and employee.can_process_orders:
            order.processed_by = employee

        order.save()

        messages.success(
            self.request,
            f"{employee.user.get_full_name()} has been assigned to this order as {self.object.get_role_display()}",
        )
        return response

    def get_success_url(self):
        return reverse_lazy(
            "bloom:order_detail", kwargs={"pk": self.kwargs["order_pk"]}
        )


class CompleteAssignmentView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        assignment = get_object_or_404(EmployeeOrderAssignment, pk=pk)
        notes = request.POST.get("notes", "")

        # Complete the assignment
        assignment.complete_assignment(notes)

        messages.success(
            request,
            f"Assignment for {assignment.employee.user.get_full_name()} has been marked as completed",
        )

        return redirect("bloom:order_detail", pk=assignment.order.pk)
