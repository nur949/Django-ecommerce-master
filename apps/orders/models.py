from django.db import models
from django.conf import settings
from apps.cart.models import OrderItem
from apps.users.models import BillingAddress
from apps.payments.models import Payment

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        BillingAddress, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        BillingAddress, related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username if self.user else f"Guest - {self.ref_code}"

    def get_subtotal(self):
        subtotal = 0
        for order_item in self.items.all():
            subtotal += order_item.get_final_price()
        if self.coupon:
            subtotal -= self.coupon.amount
        return subtotal

    def get_shipping_cost(self):
        subtotal = self.get_subtotal()
        from apps.products.models import SiteConfiguration
        config = SiteConfiguration.objects.first()
        if config:
            if subtotal >= config.free_shipping_threshold:
                return 0.0
            return config.shipping_cost
        return 60.0  # Fallback shipping cost

    def get_total(self):
        return self.get_subtotal() + self.get_shipping_cost()


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f'{self.pk}'

