from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def calculate_tax(value, rate=0.07):
    """Calculate tax amount from a value using the given rate (default 7%)"""
    if value:
        try:
            return (Decimal(str(value)) * Decimal(str(rate))).quantize(Decimal("0.01"))
        except:
            return 0
    return 0
