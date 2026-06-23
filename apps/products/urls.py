from django.urls import path
from .views import (
    HomeView, ShopView, ItemDetailView, CategoryView, category_list_api, product_search_api,
    toggle_wishlist_ajax, wishlist_info_api, WishlistSummaryView, auth_status_api
)

app_name = 'products'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('category/<slug>/', CategoryView.as_view(), name='category'),
    path('api/categories/', category_list_api, name='api-categories'),
    path('api/search/', product_search_api, name='api-search'),
    path('api/wishlist/toggle/<slug>/', toggle_wishlist_ajax, name='api-wishlist-toggle'),
    path('api/wishlist/info/', wishlist_info_api, name='api-wishlist-info'),
    path('wishlist/', WishlistSummaryView.as_view(), name='wishlist-summary'),
    path('api/auth/status/', auth_status_api, name='api-auth-status'),
]

