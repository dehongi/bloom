from django.shortcuts import render
from shop.models import Category, Product


def home(request):
    """
    Home page view with responsive optimizations, featured products and categories.
    """
    context = {}

    # Add featured products and categories for the homepage
    context["featured_products"] = Product.objects.filter(
        featured=True, is_active=True
    )[:8]
    context["featured_categories"] = Category.objects.filter(featured=True)[:4]

    # Add PWA and mobile-specific metadata
    context["meta"] = {
        "title": "Bloom - Home",
        "description": "Welcome to Bloom - Your one-stop shop for beautiful flowers and gifts",
        "viewport": "width=device-width, initial-scale=1, maximum-scale=5",
        "theme_color": "#0d6efd",  # Bootstrap primary color
    }

    return render(request, "website/home.html", context)


def about(request):
    """About page with app info."""
    return render(
        request,
        "website/about.html",
        {
            "meta": {
                "title": "About Bloom",
                "description": "Learn about our floral and gift shop",
            }
        },
    )


def contact(request):
    """Contact page."""
    return render(
        request,
        "website/contact.html",
        {
            "meta": {
                "title": "Contact Us",
                "description": "Get in touch with our floral design team",
            }
        },
    )


def terms(request):
    """Terms page."""
    return render(
        request,
        "website/terms.html",
        {
            "meta": {
                "title": "Terms of Service",
                "description": "Our terms and conditions",
            }
        },
    )


def privacy(request):
    """Privacy policy."""
    return render(
        request,
        "website/privacy.html",
        {
            "meta": {
                "title": "Privacy Policy",
                "description": "How we protect your data",
            }
        },
    )


def faq(request):
    """FAQ page with mobile-friendly layout."""
    return render(
        request,
        "website/faq.html",
        {
            "meta": {
                "title": "Frequently Asked Questions",
                "description": "Get answers about Bloom's products and services",
                "mobile_app": True,
            }
        },
    )
