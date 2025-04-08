from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    # Cart URLs
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    # Checkout URLs
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("checkout/confirm/", views.checkout_confirm, name="checkout_confirm"),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path(
        "order/success/<str:order_number>/",
        views.OrderSuccessView.as_view(),
        name="order_success",
    ),
    # Order management
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path(
        "order/<str:order_number>/",
        views.OrderDetailView.as_view(),
        name="order_detail",
    ),
    # Review
    path("product/<slug:slug>/review/", views.add_review, name="add_review"),
]
