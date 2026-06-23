from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from .models import OrderItem

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['display_image', 'user', 'item', 'quantity', 'ordered', 'final_price']
    list_filter = ['ordered', 'item__category']
    search_fields = ['user__username', 'item__title']

    def display_image(self, obj):
        if obj.item and obj.item.image:
            return mark_safe(f'<img src="{obj.item.image.url}" class="w-10 h-10 rounded-lg object-cover border border-slate-200 dark:border-zinc-800 shadow-sm" />')
        return mark_safe('<div class="w-10 h-10 rounded-lg bg-slate-100 dark:bg-zinc-800 flex items-center justify-center text-xs text-slate-400">No Image</div>')
    display_image.short_description = 'Image'

    def final_price(self, obj):
        try:
            return f"৳{obj.get_final_price()}"
        except Exception:
            return "৳0.00"
    final_price.short_description = 'Final Price'

    fieldsets = (
        ('User & Status', {
            'fields': ('user', 'ordered')
        }),
        ('Product details', {
            'fields': ('item', 'quantity')
        }),
    )
