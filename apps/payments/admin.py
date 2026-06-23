from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ['stripe_charge_id', 'payment_method', 'user', 'amount', 'timestamp']
    list_filter = ['payment_method', 'timestamp']
    search_fields = ['stripe_charge_id', 'user__username', 'payment_method']
    readonly_fields = ['timestamp']

    fieldsets = (
        ('Transaction Info', {
            'fields': ('stripe_charge_id', 'payment_method', 'user', 'amount', 'timestamp')
        }),
    )
