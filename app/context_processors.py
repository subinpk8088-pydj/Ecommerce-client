from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import Cart, CartItem

User = get_user_model()

def cart_processor(request):
    cart_count = 0
    if request.user.is_authenticated:
        # Get the user's cart first, then find cart items
        try:
            cart = Cart.objects.get(user=request.user)
            # Sum the quantities of all items in the cart
            cart_items_sum = CartItem.objects.filter(cart=cart).aggregate(
                total_items=Sum('quantity')
            )
            cart_count = cart_items_sum['total_items'] or 0
        except Cart.DoesNotExist:
            # No cart exists yet
            cart_count = 0
            
    return {'cart_count': cart_count}