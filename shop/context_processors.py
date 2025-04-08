from .models import Category, Cart


def shop_context(request):
    """
    Context processor to add cart and categories to all templates.
    """
    # Get categories for the navigation menu
    categories = Category.objects.filter(parent=None)

    # Get or initialize cart for the current user
    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if session_id:
            cart = Cart.objects.filter(session_id=session_id).first()

    return {
        "categories": categories,
        "cart": cart,
    }
