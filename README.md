# Bloom

A comprehensive Django web application for managing flowers, orders, customers, and e-commerce operations. Bloom provides an integrated platform for handling customer relationships, product management, order processing, and shop operations.

## Overview

Bloom is a multi-module Django project designed to manage:

- **Customer Relationships**: Track customers, vendors, partners, and contacts
- **Product Management**: Manage flower products, types, occasions, and inventory
- **Order Management**: Process and track orders with detailed status workflows
- **E-Commerce**: Shopping cart, product catalog, reviews, and coupons
- **User Accounts**: Custom user authentication and authorization

## Features

### Core Modules

#### 📋 **Bloom** (Main Business Logic)

- Customer and contact person management
- Product and product type management
- Occasion-based product categorization
- Order management with workflow tracking
- Delivery method configuration
- Employee order assignments
- Custom fields for flexible data storage
- Contact relationships and hierarchies

#### 🛍️ **Shop** (E-Commerce)

- Product catalog and categories
- Shopping cart functionality
- Order processing and tracking
- Product reviews and ratings
- Coupon and discount system
- Coupon usage tracking
- Product variants and availability

#### 👤 **Accounts** (Authentication)

- Custom user model with email-based authentication
- User profile management
- Password management
- User authentication and authorization
- Integration with Django admin

#### 🌐 **Website** (Frontend)

- Public website functionality
- Customer-facing interfaces
- Static pages and content management

## Tech Stack

- **Framework**: Django 5.2
- **Database**: SQLite (default, configurable)
- **Python**: 3.x
- **Image Processing**:
  - django-imagekit (5.0.0) - Image processing pipeline
  - Pillow (11.1.0) - Python Imaging Library
  - pilkit (3.0) - Image processing toolkit
- **Additional Libraries**:
  - django-appconf (1.1.0) - App configuration management
  - django-cleanup (9.0.0) - Automatic media file cleanup
  - asgiref (3.8.1) - ASGI utilities
  - sqlparse (0.5.3) - SQL parser

## Project Structure

```
bloom/
├── accounts/              # User authentication and accounts
│   ├── models.py         # Custom user model
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── migrations/
├── bloom/                # Main business logic
│   ├── models.py         # Customer, Product, Order models
│   ├── views.py          # Business logic views
│   ├── forms.py
│   ├── signals.py
│   ├── urls.py
│   ├── fixtures/         # Sample data
│   ├── management/       # Custom Django commands
│   └── migrations/
├── shop/                 # E-commerce functionality
│   ├── models.py         # Shop products, orders, coupons
│   ├── views.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── signals.py
│   ├── urls.py
│   ├── templatetags/     # Custom template tags
│   └── migrations/
├── website/              # Public website
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── django_project/       # Django configuration
│   ├── settings.py       # Project settings
│   ├── urls.py           # URL routing
│   ├── wsgi.py
│   └── asgi.py
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── media/                # User-uploaded content
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── db.sqlite3           # SQLite database
```

## Installation

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Virtual environment tool (venv)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd bloom
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**

   ```bash
   python manage.py loaddata bloom/fixtures/*.json
   ```

7. **Run development server**

   ```bash
   python manage.py runserver
   ```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` with your superuser credentials to:

- Manage users and permissions
- Create and edit products
- View and process orders
- Manage customers and contacts
- Configure delivery methods
- View order statuses and workflows

### Key URLs

- **Home**: `/` - Website homepage
- **Shop**: `/shop/` - Product catalog and shopping
- **Accounts**: `/accounts/` - Login, registration, password management
- **Bloom**: `/bloom/` - Business management features
- **Admin**: `/admin/` - Django administration panel

## Models

### Core Models

- **CustomUser**: Extended Django user model with email authentication
- **Customer**: Customer information with contact details and company data
- **ContactPerson**: Individual contacts associated with customers
- **Product**: Product catalog with descriptions and pricing
- **ProductType**: Product categorization
- **Occasion**: Event-based product tagging (e.g., Wedding, Birthday)
- **Order**: Order management with status tracking
- **OrderItem**: Individual items within orders
- **DeliveryMethod**: Shipping and delivery options
- **Coupon**: Discount codes and promotions
- **Review**: Customer product reviews and ratings

## Database Migrations

The project includes migrations for:

- Initial schema setup
- Customer model evolution
- Order and shop integration
- Contact person relationships
- Employee order assignments
- Product variant management

Run migrations with:

```bash
python manage.py migrate
```

## Configuration

Edit `django_project/settings.py` to configure:

- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: Add domain names for production
- **DATABASES**: Configure database connection
- **SECRET_KEY**: Change from default insecure key
- **Email Settings**: Configure email backend
- **Static Files**: Configure static file serving

### Important Security Notes

⚠️ **Before deploying to production**:

1. Change `SECRET_KEY` to a secure value
2. Set `DEBUG = False`
3. Update `ALLOWED_HOSTS` with your domain
4. Configure proper email settings
5. Use a production database (PostgreSQL recommended)
6. Enable HTTPS and secure cookies

## Development

### Creating Custom Django Commands

Place custom management commands in `bloom/management/commands/` or `shop/management/commands/`

### Template Tags

Custom template filters are available in `shop/templatetags/shop_filters.py`

### Signals

Models use Django signals for automatic operations:

- `bloom/signals.py` - Bloom app signals
- `shop/signals.py` - Shop app signals

## Testing

Run tests with:

```bash
python manage.py test
```

Test files are located in:

- `accounts/tests.py`
- `bloom/tests.py`
- `shop/tests.py`
- `website/tests.py`

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn django_project.wsgi:application --bind 0.0.0.0:8000
```

### Using WSGI

The WSGI application is configured in `django_project/wsgi.py`

### Environment Variables

Use environment variables for sensitive configuration:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `EMAIL_HOST_PASSWORD`

### Static Files

Collect static files for production:

```bash
python manage.py collectstatic
```

## Troubleshooting

### Database Issues

```bash
# Reset migrations (development only)
python manage.py migrate zero <app_name>
python manage.py migrate <app_name>
```

### Media Files

The `django-cleanup` package automatically removes orphaned media files when model instances are deleted.

### Image Processing

Images are processed using django-imagekit. Ensure Pillow is properly installed:

```bash
pip install --upgrade Pillow
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests to ensure nothing breaks
4. Commit with clear messages
5. Push to the repository

## License

[Specify your license here]

## Support

For issues, questions, or contributions, please contact [contact information].

---

**Last Updated**: December 2024
**Django Version**: 5.2
**Python Version**: 3.10+
