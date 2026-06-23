from django import template
from apps.orders.models import Order

register = template.Library()

def get_active_cart(request):
    if request.user.is_authenticated:
        qs = Order.objects.filter(user=request.user, ordered=False)
        if qs.exists():
            return qs[0]
    else:
        session_order_id = request.session.get('order_id')
        if session_order_id:
            try:
                return Order.objects.get(id=session_order_id, ordered=False)
            except Order.DoesNotExist:
                return None
    return None

@register.simple_tag
def cart_item_count(request):
    if not request:
        return 0
    order = get_active_cart(request)
    if order:
        return order.items.count()
    return 0

@register.simple_tag
def get_active_order(request):
    if not request:
        return None
    return get_active_cart(request)
