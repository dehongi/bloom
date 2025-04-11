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
- `employees.json` - Staff members with different roles
- `orders.json` - Sample orders
- `order_items.json` - Items within orders
- `order_statuses.json` - Order status history
- `custom_fields.json` - Custom fields for orders
- `coupons.json` - Sample discount coupons
- `coupon_usages.json` - Records of coupon usage by users

## Loading Fixtures

To load all fixtures, run the following command:

```bash
python manage.py loaddata users occasions product_types products delivery_methods customers employees orders order_items order_statuses custom_fields products_occasions coupons coupon_usages
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
7. `employees.json` (Employee model - depends on users)
8. `orders.json` (Order model - depends on customers, delivery methods, and occasions)
9. `order_items.json` (OrderItem model - depends on orders and products)
10. `order_statuses.json` (OrderStatus model - depends on orders and users)
11. `custom_fields.json` (CustomField model - depends on orders)
12. `products_occasions.json` (Many-to-many relationship - depends on products and occasions)
13. `coupons.json` (Coupon model)
14. `coupon_usages.json` (CouponUsage model - depends on coupons, users, and orders)

## Important Notes

- **CouponUsage Order Field**: The `order` field in `coupon_usages.json` is intentionally set to `null` because the `shop.couponusage` model cannot directly reference orders from the `bloom.order` model as they are in different apps.

## Password for User Accounts

All sample user accounts use the password: `password123`

- Admin User: <admin@example.com>
- Store Manager: <manager@example.com>
- Regular User: <user@example.com>
