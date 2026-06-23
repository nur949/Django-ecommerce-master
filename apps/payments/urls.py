from django.urls import path
from .views import PaymentView

app_name = 'payments'

urlpatterns = [
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
]
