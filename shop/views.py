from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from decimal import Decimal

# Configure logger
logger = logging.getLogger(__name__)

from .models import (
    Category,
    Product,
    ProductVariant,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
    Coupon,
    CouponUsage,
)

# Create your views here.


# Category Views
class CategoryDetailView(DetailView):
    model = Category
    template_name = "shop/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include all products from this category and its subcategories
        category_ids = [self.object.id]
        for child in self.object.children.all():
            category_ids.append(child.id)

        context["products"] = Product.objects.filter(
            categories__id__in=category_ids, is_active=True
        ).distinct()
        return context


# Product Views
class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        # Filter by search query
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(categories__name__icontains=q)
            ).distinct()

        # Filter by category
        category_id = self.request.GET.get("category")
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                category_ids = [category.id]
                for child in category.children.all():
                    category_ids.append(child.id)
                queryset = queryset.filter(categories__id__in=category_ids).distinct()
            except Category.DoesNotExist:
                pass

        # Sort products
        sort = self.request.GET.get("sort", "newest")
        if sort == "price_low":
            queryset = queryset.order_by("price")
        elif sort == "price_high":
            queryset = queryset.order_by("-price")
        elif sort == "name":
            queryset = queryset.order_by("name")
        else:  # newest
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(parent=None)
        context["sort"] = self.request.GET.get("sort", "newest")
        context["q"] = self.request.GET.get("q", "")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["variants"] = self.object.variants.filter(is_active=True)
        context["related_products"] = (
            Product.objects.filter(
                categories__in=self.object.categories.all(), is_active=True
            )
            .exclude(id=self.object.id)
            .distinct()[:4]
        )
        context["reviews"] = self.object.reviews.filter(is_approved=True)

        # Check if user has already reviewed this product
        if self.request.user.is_authenticated:
            context["user_review"] = self.object.reviews.filter(
                user=self.request.user
            ).first()

        return context


# Cart Views
class CartView(View):
    template_name = "shop/cart.html"

    def get(self, request):
        cart = self._get_cart(request)
        return render(request, self.template_name, {"cart": cart})

    def _get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)
        return cart


def get_cart(request):
    """Get or create a cart for the user or session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart


def get_client_ip(request):
    """Get the client IP address from the request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@require_POST
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")
    quantity = int(request.POST.get("quantity", 1))

    # Get or create cart
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)

    # Get product and variant
    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    if variant_id:
        variant = get_object_or_404(
            ProductVariant, id=variant_id, product=product, is_active=True
        )

    # Check stock
    if variant and variant.stock_quantity < quantity:
        messages.error(
            request, f"Sorry, we only have {variant.stock_quantity} in stock."
        )
        return JsonResponse({"status": "error", "message": "Not enough stock"})
    elif not variant and product.stock_quantity < quantity:
        messages.error(
            request, f"Sorry, we only have {product.stock_quantity} in stock."
        )
        return JsonResponse({"status": "error", "message": "Not enough stock"})

    # Add to cart
    try:
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f"{product.name} added to your cart.")
        return JsonResponse(
            {
                "status": "success",
                "cart_count": cart.count,
                "message": f"{product.name} added to your cart.",
            }
        )
    except Exception as e:
        messages.error(request, f"Error adding to cart: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)})


@require_POST
def update_cart(request):
    item_id = request.POST.get("item_id")
    quantity = int(request.POST.get("quantity", 1))

    # Get cart item
    cart_item = get_object_or_404(CartItem, id=item_id)

    # Check if this cart belongs to the user
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            messages.error(request, "You don't have permission to update this cart.")
            return JsonResponse({"status": "error", "message": "Permission denied"})
    else:
        session_id = request.session.session_key
        if cart_item.cart.session_id != session_id:
            messages.error(request, "You don't have permission to update this cart.")
            return JsonResponse({"status": "error", "message": "Permission denied"})

    # Check stock
    if cart_item.variant and cart_item.variant.stock_quantity < quantity:
        messages.error(
            request, f"Sorry, we only have {cart_item.variant.stock_quantity} in stock."
        )
        return JsonResponse({"status": "error", "message": "Not enough stock"})
    elif not cart_item.variant and cart_item.product.stock_quantity < quantity:
        messages.error(
            request, f"Sorry, we only have {cart_item.product.stock_quantity} in stock."
        )
        return JsonResponse({"status": "error", "message": "Not enough stock"})

    # Update quantity
    cart_item.quantity = quantity
    cart_item.save()

    # Get updated cart
    cart = cart_item.cart

    return JsonResponse(
        {
            "status": "success",
            "cart_count": cart.count,
            "cart_total": str(cart.total),
            "item_subtotal": str(cart_item.subtotal),
        }
    )


@require_POST
def remove_from_cart(request):
    item_id = request.POST.get("item_id")

    # Get cart item
    cart_item = get_object_or_404(CartItem, id=item_id)

    # Check if this cart belongs to the user
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            messages.error(request, "You don't have permission to update this cart.")
            return JsonResponse({"status": "error", "message": "Permission denied"})
    else:
        session_id = request.session.session_key
        if cart_item.cart.session_id != session_id:
            messages.error(request, "You don't have permission to update this cart.")
            return JsonResponse({"status": "error", "message": "Permission denied"})

    # Get cart for later use
    cart = cart_item.cart
    product_name = cart_item.product.name

    # Delete item
    cart_item.delete()

    messages.success(request, f"{product_name} removed from your cart.")
    return JsonResponse(
        {
            "status": "success",
            "cart_count": cart.count,
            "cart_total": str(cart.total),
            "message": f"{product_name} removed from your cart.",
        }
    )


# Checkout Views
class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "shop/checkout.html"

    def get(self, request, *args, **kwargs):
        cart = get_cart(request)
        if not cart or cart.count == 0:
            messages.warning(
                request, "Your cart is empty. Please add items to checkout."
            )
            return redirect("shop:product_list")

        # Check if a coupon is stored in session
        coupon_id = request.session.get("coupon_id")
        coupon_discount = request.session.get("coupon_discount", "0")

        context = self.get_context_data(**kwargs)
        context["cart"] = cart

        # Add coupon information to context if available
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                context["coupon"] = coupon
                context["discount_amount"] = Decimal(coupon_discount)
                context["total_after_discount"] = cart.total - Decimal(coupon_discount)
            except Coupon.DoesNotExist:
                # If coupon no longer exists, remove from session
                if "coupon_id" in request.session:
                    del request.session["coupon_id"]
                if "coupon_discount" in request.session:
                    del request.session["coupon_discount"]

        return self.render_to_response(context)


@require_POST
def checkout_confirm(request):
    # Get cart
    cart = get_cart(request)
    if not cart or cart.count == 0:
        messages.warning(request, "Your cart is empty. Cannot proceed with checkout.")
        return redirect("shop:cart")

    # Check if all items are in stock
    for item in cart.items.all():
        if item.product.stock_quantity < item.quantity:
            messages.error(
                request,
                f"{item.product.name} is out of stock. Please remove it from your cart.",
            )
            return redirect("shop:cart")

    # Process the form data
    form_data = request.POST

    # Create an order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=form_data.get("full_name"),
        email=form_data.get("email"),
        phone=form_data.get("phone"),
        address_line_1=form_data.get("shipping_address1"),
        address_line_2=form_data.get("shipping_address2", ""),
        city=form_data.get("shipping_city"),
        state=form_data.get("shipping_state"),
        postal_code=form_data.get("shipping_zipcode"),
        country=form_data.get("shipping_country"),
        shipping_cost=Decimal(form_data.get("shipping_cost", "0")),
        tax_amount=Decimal(form_data.get("tax_amount", "0")),
        subtotal=cart.total,
        total=cart.total,  # Will be updated
        order_notes=form_data.get("order_notes", ""),
        ip_address=get_client_ip(request),
    )

    # Check for coupon
    coupon_id = request.session.get("coupon_id")
    coupon_discount = Decimal(request.session.get("coupon_discount", "0"))

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            # Verify coupon is still valid
            if coupon.is_valid:
                # Apply coupon to order
                order.coupon = coupon
                order.discount_amount = coupon_discount

                # Record coupon usage
                if request.user.is_authenticated:
                    CouponUsage.objects.create(
                        coupon=coupon, user=request.user, order=order
                    )

                # Update coupon usage count
                coupon.times_used += 1
                coupon.save()

                # Clear coupon from session
                del request.session["coupon_id"]
                del request.session["coupon_discount"]
        except Coupon.DoesNotExist:
            # If coupon doesn't exist, just proceed without it
            pass

    # Update the total with shipping, tax, and discount
    order.total = (
        order.subtotal + order.shipping_cost + order.tax_amount - order.discount_amount
    )
    order.save()

    # Create order items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            product_name=item.product.name,
            variant_name=item.variant.name if item.variant else "",
            price=item.price,
            quantity=item.quantity,
            subtotal=item.subtotal,
        )

        # Update stock quantity
        product = item.product
        product.stock_quantity -= item.quantity
        if product.stock_quantity <= 0:
            product.in_stock = False
        product.save()

    # Clear cart
    cart.items.all().delete()

    # Note: A corresponding bloom order will be automatically created via the post_save signal
    # The signal handler in shop/signals.py will create a bloom.Order record linked to this order
    # and populate it with customer and item data for internal processing

    # Redirect to success page
    return redirect("shop:order_success", order_number=order.order_number)


@require_POST
@csrf_exempt
def apply_coupon(request):
    """
    Apply a coupon code to the session for later use in checkout.
    This is called via AJAX from the checkout page.
    """
    data = json.loads(request.body)
    coupon_code = data.get("coupon_code", "").strip().upper()

    # If no coupon code provided
    if not coupon_code:
        return JsonResponse(
            {"status": "error", "message": "Please enter a coupon code"}
        )

    try:
        # Try to get the coupon and check if it's valid
        coupon = Coupon.objects.get(code=coupon_code, active=True)

        if not coupon.is_valid:
            return JsonResponse(
                {"status": "error", "message": "This coupon is no longer valid"}
            )

        # Get the cart
        cart = get_cart(request)
        if not cart or cart.count == 0:
            return JsonResponse({"status": "error", "message": "Your cart is empty"})

        # Check minimum order value
        if cart.total < coupon.min_order_value:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"This coupon requires a minimum order of ${coupon.min_order_value}",
                }
            )

        # Check if user has already used this coupon (for single-use coupons)
        if coupon.single_use and request.user.is_authenticated:
            if CouponUsage.objects.filter(coupon=coupon, user=request.user).exists():
                return JsonResponse(
                    {"status": "error", "message": "You have already used this coupon"}
                )

        # Calculate the discount
        discount = coupon.calculate_discount(cart.total)

        # Store the coupon in session for later use during checkout
        request.session["coupon_id"] = coupon.id
        request.session["coupon_discount"] = str(discount)

        # Create a response with the discount information
        discount_type = (
            "fixed amount" if coupon.discount_type == "fixed" else "percentage"
        )
        discount_value = (
            f"${coupon.discount_value}"
            if coupon.discount_type == "fixed"
            else f"{coupon.discount_value}%"
        )

        return JsonResponse(
            {
                "status": "success",
                "message": f"Coupon applied: {discount_value} {discount_type} discount",
                "discount_amount": float(discount),
                "new_total": float(cart.total - discount),
            }
        )

    except Coupon.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Invalid coupon code"})
    except Exception as e:
        # Log the error
        logger.error(f"Error applying coupon: {str(e)}")
        return JsonResponse(
            {
                "status": "error",
                "message": "An error occurred while applying the coupon",
            }
        )


class OrderSuccessView(TemplateView):
    template_name = "shop/order_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = kwargs.get("order_number")
        order = get_object_or_404(Order, order_number=order_number)

        # Check if this order belongs to the user
        if self.request.user.is_authenticated and order.user == self.request.user:
            context["order"] = order
        elif (
            not self.request.user.is_authenticated
            and "recent_order" in self.request.session
            and self.request.session["recent_order"] == order_number
        ):
            context["order"] = order
        else:
            context["error"] = "You don't have permission to view this order."

        return context


# Order Management
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shop/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "shop/order_detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Reviews
@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Check if user already reviewed this product
    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == "POST":
        title = request.POST.get("title")
        body = request.POST.get("body")
        rating = int(request.POST.get("rating", 5))

        if existing_review:
            # Update existing review
            existing_review.title = title
            existing_review.body = body
            existing_review.rating = rating
            existing_review.is_approved = False  # Require re-approval
            existing_review.save()
            messages.success(
                request, "Your review has been updated and is pending approval."
            )
        else:
            # Create new review
            Review.objects.create(
                product=product,
                user=request.user,
                title=title,
                body=body,
                rating=rating,
            )
            messages.success(
                request, "Your review has been submitted and is pending approval."
            )

        return redirect("shop:product_detail", slug=slug)

    # If GET request, show form with existing review data if any
    context = {"product": product, "review": existing_review}
    return render(request, "shop/add_review.html", context)
