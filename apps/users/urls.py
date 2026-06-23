from django.urls import path
from .views import ProfileView, OrderHistoryView

app_name = 'users'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile-detail'),
    path('profile/orders/', OrderHistoryView.as_view(), name='order-history'),
]
