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
from django.db.models import Q, Sum
from django.forms import inlineformset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone

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
)
from .forms import (
    CustomerForm,
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

            # Create status history entry
            OrderStatus.objects.create(
                order=order, status=new_status, notes=notes, updated_by=request.user
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

        # Get orders by day for the last 30 days
        today = timezone.now().date()
        thirty_days_ago = today - timezone.timedelta(days=30)

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
