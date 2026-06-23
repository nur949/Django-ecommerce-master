from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import View
from django.http import JsonResponse
from apps.products.models import Item, Variation
from apps.orders.models import Order
from .models import OrderItem

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

def get_or_create_active_cart(request):
    if request.user.is_authenticated:
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            session_order_id = request.session.get('order_id')
            if session_order_id:
                try:
                    session_order = Order.objects.get(id=session_order_id, ordered=False)
                    for item in session_order.items.all():
                        item.user = request.user
                        item.save()
                        if not order.items.filter(item=item.item).exists():
                            order.items.add(item)
                        else:
                            user_item = order.items.get(item=item.item)
                            user_item.quantity += item.quantity
                            user_item.save()
                            item.delete()
                    session_order.delete()
                    del request.session['order_id']
                except Order.DoesNotExist:
                    pass
            return order
        else:
            session_order_id = request.session.get('order_id')
            if session_order_id:
                try:
                    order = Order.objects.get(id=session_order_id, ordered=False)
                    order.user = request.user
                    order.save()
                    for item in order.items.all():
                        item.user = request.user
                        item.save()
                    del request.session['order_id']
                    return order
                except Order.DoesNotExist:
                    pass
            order = Order.objects.create(user=request.user, ordered_date=timezone.now())
            return order
    else:
        session_order_id = request.session.get('order_id')
        if session_order_id:
            try:
                return Order.objects.get(id=session_order_id, ordered=False)
            except Order.DoesNotExist:
                pass
        order = Order.objects.create(user=None, ordered_date=timezone.now())
        request.session['order_id'] = order.id
        return order

class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/users/profile/#cart')
        order = get_active_cart(self.request)
        if order:
            context = {'object': order}
            return render(self.request, 'order_summary.html', context)
        else:
            messages.info(self.request, 'You do not have an active order')
            return redirect('/')

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = get_or_create_active_cart(request)
    
    # Extract variations from POST or GET
    selected_variations = []
    if request.method == 'POST':
        for category in ['size', 'color']:
            val = request.POST.get(category)
            if val and val != "Choose an option":
                try:
                    variation = item.variations.get(category=category, title__iexact=val, active=True)
                    selected_variations.append(variation)
                except Variation.DoesNotExist:
                    pass
        qty = request.POST.get('num-product', '1')
        try:
            quantity = int(qty)
        except ValueError:
            quantity = 1
    else:
        for category in ['size', 'color']:
            val = request.GET.get(category)
            if val and val != "Choose an option":
                try:
                    variation = item.variations.get(category=category, title__iexact=val, active=True)
                    selected_variations.append(variation)
                except Variation.DoesNotExist:
                    pass
        quantity = 1

    # Check if an OrderItem with exact same variations already exists
    order_item = None
    cart_items = order.items.filter(item=item)
    for ci in cart_items:
        if set(ci.variations.all()) == set(selected_variations):
            order_item = ci
            break

    if order_item:
        order_item.quantity += quantity
        order_item.save()
        messages.info(request, 'Item quantity was updated.')
    else:
        order_item = OrderItem.objects.create(
            item=item,
            user=request.user if request.user.is_authenticated else None,
            ordered=False,
            quantity=quantity
        )
        order_item.variations.set(selected_variations)
        order_item.save()
        order.items.add(order_item)
        messages.info(request, 'Item was added to your cart.')
        
    return redirect('cart:order-summary')

def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = get_active_cart(request)
    if order:
        order_item_qs = order.items.filter(item__slug=item.slug)
        if order_item_qs.exists():
            order_item = order_item_qs[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, 'Item was removed from your cart.')
            return redirect('cart:order-summary')
        else:
            messages.info(request, 'Item was not in your cart.')
            return redirect('products:product', slug=slug)
    else:
        messages.info(request, 'You do not have an active order.')
        return redirect('products:product', slug=slug)

def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = get_active_cart(request)
    if order:
        order_item_qs = order.items.filter(item__slug=item.slug)
        if order_item_qs.exists():
            order_item = order_item_qs[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.info(request, 'This item quantity was updated.')
            return redirect('cart:order-summary')
        else:
            messages.info(request, 'Item was not in your cart.')
            return redirect('products:product', slug=slug)
    else:
        messages.info(request, 'You do not have an active order.')
        return redirect('products:product', slug=slug)


def cart_info_api(request):
    order = get_active_cart(request)
    if not order:
        return JsonResponse({'items': [], 'total': "৳0.00", 'count': 0})
        
    items_data = []
    for order_item in order.items.all():
        items_data.append({
            'id': order_item.id,
            'title': order_item.item.title,
            'slug': order_item.item.slug,
            'quantity': order_item.quantity,
            'price': f"৳{order_item.item.price:.2f}",
            'discount_price': f"৳{order_item.item.discount_price:.2f}" if order_item.item.discount_price else None,
            'total_price': f"৳{order_item.get_final_price():.2f}",
            'saved_amount': f"৳{order_item.get_amount_saved():.2f}" if order_item.item.discount_price else None,
            'image': order_item.item.image.url if order_item.item.image else '',
            'variations': [{'category': v.category, 'title': v.title, 'price_modifier': v.price_modifier} for v in order_item.variations.all()]
        })
        
    return JsonResponse({
        'items': items_data,
        'total': f"৳{order.get_total():.2f}",
        'count': order.items.count(),
        'coupon': {
            'code': order.coupon.code,
            'amount': f"৳{order.coupon.amount:.2f}"
        } if order.coupon else None
    })

def add_to_cart_ajax(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = get_or_create_active_cart(request)
    
    order_item_qs = order.items.filter(item__slug=item.slug)
    if order_item_qs.exists():
        order_item = order_item_qs[0]
        order_item.quantity += 1
        order_item.save()
    else:
        order_item = OrderItem.objects.create(
            item=item,
            user=request.user if request.user.is_authenticated else None,
            ordered=False
        )
        order.items.add(order_item)
        
    return cart_info_api(request)

def remove_single_item_from_cart_ajax(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = get_active_cart(request)
    if order:
        order_item_qs = order.items.filter(item__slug=item.slug)
        if order_item_qs.exists():
            order_item = order_item_qs[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
    return cart_info_api(request)

def remove_from_cart_ajax(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = get_active_cart(request)
    if order:
        order_item_qs = order.items.filter(item__slug=item.slug)
        if order_item_qs.exists():
            order_item = order_item_qs[0]
            order.items.remove(order_item)
            order_item.delete()
    return cart_info_api(request)

