from django.db import models
from django.conf import settings
from apps.products.models import Item

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    variations = models.ManyToManyField('products.Variation', blank=True)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
        modifiers = sum(v.price_modifier for v in self.variations.all())
        return self.quantity * (self.item.price + modifiers)

    def get_total_discount_item_price(self):
        if self.item.discount_price:
            modifiers = sum(v.price_modifier for v in self.variations.all())
            return self.quantity * (self.item.discount_price + modifiers)
        return self.get_total_item_price()

    def get_amount_saved(self):
        if self.item.discount_price:
            return (self.quantity * self.item.price) - (self.quantity * self.item.discount_price)
        return 0.0

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
