from .views import CartService

def cart_count(request):
    if 'admin' in request.path:
        return {}
    cart_service = CartService(request)
    summary = cart_service.get_cart_summary()
    return {'cart_total_quantity': summary['total_items']}