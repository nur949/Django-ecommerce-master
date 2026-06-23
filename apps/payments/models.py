from django.db import models
from django.conf import settings

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='Stripe')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Guest"
        return f'{username} - {self.payment_method} - ৳{self.amount}'
