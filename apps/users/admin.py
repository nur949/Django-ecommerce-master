from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import BillingAddress, UserProfile

@admin.register(BillingAddress)
class BillingAddressAdmin(ModelAdmin):
    list_display = ['user', 'street_address', 'apartment_address', 'country', 'zip', 'district', 'phone_number', 'address_type', 'default']
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user__username', 'street_address', 'apartment_address', 'zip', 'phone_number']

    fieldsets = (
        ('User & Contact Details', {
            'fields': ('user', 'phone_number')
        }),
        ('Address Information', {
            'fields': ('street_address', 'apartment_address', 'country', 'zip', 'district')
        }),
        ('Preferences', {
            'fields': ('address_type', 'default')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ['user', 'phone_number', 'address']
    search_fields = ['user__username', 'user__email', 'phone_number']

