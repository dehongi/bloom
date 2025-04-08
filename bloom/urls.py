from django.urls import path
from . import views

app_name = "bloom"

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Customer URLs
    path("customers/", views.CustomerListView.as_view(), name="customer_list"),
    path("customers/new/", views.CustomerCreateView.as_view(), name="customer_create"),
    path(
        "customers/<int:pk>/",
        views.CustomerDetailView.as_view(),
        name="customer_detail",
    ),
    path(
        "customers/<int:pk>/edit/",
        views.CustomerUpdateView.as_view(),
        name="customer_update",
    ),
    path(
        "customers/<int:pk>/delete/",
        views.CustomerDeleteView.as_view(),
        name="customer_delete",
    ),
    # Occasion URLs
    path("occasions/", views.OccasionListView.as_view(), name="occasion_list"),
    path("occasions/new/", views.OccasionCreateView.as_view(), name="occasion_create"),
    path(
        "occasions/<int:pk>/edit/",
        views.OccasionUpdateView.as_view(),
        name="occasion_update",
    ),
    path(
        "occasions/<int:pk>/delete/",
        views.OccasionDeleteView.as_view(),
        name="occasion_delete",
    ),
    # Product Type URLs
    path(
        "product-types/", views.ProductTypeListView.as_view(), name="product_type_list"
    ),
    path(
        "product-types/new/",
        views.ProductTypeCreateView.as_view(),
        name="product_type_create",
    ),
    path(
        "product-types/<int:pk>/edit/",
        views.ProductTypeUpdateView.as_view(),
        name="product_type_update",
    ),
    path(
        "product-types/<int:pk>/delete/",
        views.ProductTypeDeleteView.as_view(),
        name="product_type_delete",
    ),
    # Product URLs
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/new/", views.ProductCreateView.as_view(), name="product_create"),
    path(
        "products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path(
        "products/<int:pk>/edit/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    # Delivery Method URLs
    path(
        "delivery-methods/",
        views.DeliveryMethodListView.as_view(),
        name="delivery_method_list",
    ),
    path(
        "delivery-methods/new/",
        views.DeliveryMethodCreateView.as_view(),
        name="delivery_method_create",
    ),
    path(
        "delivery-methods/<int:pk>/edit/",
        views.DeliveryMethodUpdateView.as_view(),
        name="delivery_method_update",
    ),
    path(
        "delivery-methods/<int:pk>/delete/",
        views.DeliveryMethodDeleteView.as_view(),
        name="delivery_method_delete",
    ),
    # Order URLs
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/new/", views.OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/edit/", views.OrderUpdateView.as_view(), name="order_update"),
    path(
        "orders/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"
    ),
    path(
        "orders/<int:pk>/update-status/",
        views.UpdateOrderStatusView.as_view(),
        name="update_order_status",
    ),
    # Custom Field URLs
    path(
        "orders/<int:order_pk>/custom-fields/add/",
        views.CustomFieldCreateView.as_view(),
        name="custom_field_create",
    ),
    path(
        "custom-fields/<int:pk>/edit/",
        views.CustomFieldUpdateView.as_view(),
        name="custom_field_update",
    ),
    path(
        "custom-fields/<int:pk>/delete/",
        views.CustomFieldDeleteView.as_view(),
        name="custom_field_delete",
    ),
    # AJAX URLs
    path(
        "api/product-info/", views.GetProductInfoView.as_view(), name="get_product_info"
    ),
]
