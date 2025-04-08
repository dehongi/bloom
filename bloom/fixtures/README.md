# Bloom Fixtures

This directory contains fixture data for the Bloom application. The fixtures provide sample data for testing and development purposes.

## Available Fixtures

- `users.json` - Sample user accounts
- `occasions.json` - Flower occasions (Birthday, Anniversary, etc.)
- `product_types.json` - Types of products (Bouquet, Plant, etc.)
- `products.json` - Sample flower products
- `products_occasions.json` - Many-to-many relationships between products and occasions
- `delivery_methods.json` - Delivery methods and pricing
- `customers.json` - Sample customers
- `orders.json` - Sample orders
- `order_items.json` - Items within orders
- `order_statuses.json` - Order status history
- `custom_fields.json` - Custom fields for orders
- `coupons.json` - Sample discount coupons
- `coupon_usages.json` - Records of coupon usage by users

## Loading Fixtures

To load all fixtures, run the following command:

```bash
python manage.py loaddata users occasions product_types products delivery_methods customers orders order_items order_statuses custom_fields products_occasions coupons coupon_usages
```

If you want to load specific fixtures, you can specify them:

```bash
python manage.py loaddata occasions product_types products
```

## Order of Loading

When loading all fixtures, it's important to maintain the proper order due to dependencies:

1. `users.json` (CustomUser model)
2. `occasions.json` (Occasion model)
3. `product_types.json` (ProductType model)
4. `products.json` (Product model)
5. `delivery_methods.json` (DeliveryMethod model)
6. `customers.json` (Customer model - depends on users)
7. `orders.json` (Order model - depends on customers, delivery methods, and occasions)
8. `order_items.json` (OrderItem model - depends on orders and products)
9. `order_statuses.json` (OrderStatus model - depends on orders and users)
10. `custom_fields.json` (CustomField model - depends on orders)
11. `products_occasions.json` (Many-to-many relationship - depends on products and occasions)
12. `coupons.json` (Coupon model)
13. `coupon_usages.json` (CouponUsage model - depends on coupons, users, and orders)

## Password for User Accounts

All sample user accounts use the password: `password123`

- Admin User: <admin@example.com>
- Store Manager: <manager@example.com>
- Regular User: <user@example.com>
