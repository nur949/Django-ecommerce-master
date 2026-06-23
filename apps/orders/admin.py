from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Order, Coupon, Refund

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted=True)
make_refund_accepted.short_description = 'Update orders to refund granted'

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['ref_code', 'user', 'ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'coupon']
    list_display_links = ['ref_code', 'user']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']
    search_fields = ['user__username', 'ref_code']
    actions = [make_refund_accepted]
    filter_horizontal = ('items',)

    fieldsets = (
        ('Order Identification', {
            'fields': ('user', 'ref_code', 'items')
        }),
        ('Delivery Status', {
            'fields': ('ordered', 'being_delivered', 'received')
        }),
        ('Payment & Discount', {
            'fields': ('payment', 'coupon')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Refund Status', {
            'fields': ('refund_requested', 'refund_granted')
        }),
    )

@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ['code', 'amount']
    search_fields = ['code']

@admin.register(Refund)
class RefundAdmin(ModelAdmin):
    list_display = ['order', 'email', 'accepted']
    list_filter = ['accepted']
    search_fields = ['email', 'order__ref_code']

