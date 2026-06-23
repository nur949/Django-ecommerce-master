from django.urls import path
from .views import (
    OrderSummaryView, add_to_cart, remove_from_cart, remove_single_item_from_cart,
    cart_info_api, add_to_cart_ajax, remove_single_item_from_cart_ajax, remove_from_cart_ajax
)

app_name = 'cart'

urlpatterns = [
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('api/info/', cart_info_api, name='api-info'),
    path('api/add/<slug>/', add_to_cart_ajax, name='api-add'),
    path('api/remove-single/<slug>/', remove_single_item_from_cart_ajax, name='api-remove-single'),
    path('api/remove/<slug>/', remove_from_cart_ajax, name='api-remove'),
]
