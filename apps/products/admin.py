from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from .models import Slide, Category, Item, Variation, SiteConfiguration, Wishlist, PromoBanner, ItemMedia

class VariationInline(TabularInline):
    model = Variation
    extra = 1
    fields = ('category', 'title', 'price_modifier', 'active')

class ItemMediaInline(TabularInline):
    model = ItemMedia
    extra = 1
    fields = ('media_type', 'file', 'video_url', 'thumbnail', 'image_alt', 'order')

@admin.register(Slide)
class SlideAdmin(ModelAdmin):
    list_display = ['display_image', 'caption1', 'caption2', 'link', 'is_active']
    list_filter = ['is_active']
    search_fields = ['caption1', 'caption2', 'link']
    fields = ('caption1', 'caption2', 'link', 'image', 'image_alt', 'is_active')

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="w-16 h-8 rounded object-cover border border-slate-200 dark:border-zinc-800 shadow-sm" />')
        return mark_safe('<div class="w-16 h-8 rounded bg-slate-100 dark:bg-zinc-800 flex items-center justify-center text-xs text-slate-400">No Image</div>')
    display_image.short_description = 'Slide Image'

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['display_image', 'title', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('General Info', {
            'fields': ('title', 'slug', 'parent', 'description', 'image', 'is_active')
        }),
        ('SEO Optimization', {
            'fields': ('seo_meta_title', 'seo_meta_description', 'seo_meta_keywords', 'image_alt'),
            'classes': ('collapse',),
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="w-10 h-10 rounded-lg object-cover border border-slate-200 dark:border-zinc-800 shadow-sm" />')
        return mark_safe('<div class="w-10 h-10 rounded-lg bg-slate-100 dark:bg-zinc-800 flex items-center justify-center text-xs text-slate-400">No Image</div>')
    display_image.short_description = 'Image'

@admin.register(Item)
class ItemAdmin(ModelAdmin):
    list_display = ['display_image', 'title', 'price', 'discount_price', 'category', 'label', 'stock_no', 'is_active']
    list_filter = ['category', 'label', 'is_active']
    search_fields = ['title', 'description_short', 'description_long', 'stock_no']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [VariationInline, ItemMediaInline]

    fieldsets = (
        ('General Information', {
            'fields': ('title', 'slug', 'category', 'stock_no', 'is_active')
        }),
        ('Pricing Info', {
            'fields': ('price', 'discount_price')
        }),
        ('Media & Badge', {
            'fields': ('image', 'label')
        }),
        ('Detailed Descriptions', {
            'fields': ('description_short', 'description_long')
        }),
        ('SEO Optimization (Search & Social Share)', {
            'fields': (
                'seo_meta_title',
                'seo_meta_description',
                'seo_meta_keywords',
                'seo_og_title',
                'seo_og_description',
                'seo_og_image',
                'seo_schema_markup'
            ),
            'classes': ('collapse',),
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="w-10 h-10 rounded-lg object-cover border border-slate-200 dark:border-zinc-800 shadow-sm" />')
        return mark_safe('<div class="w-10 h-10 rounded-lg bg-slate-100 dark:bg-zinc-800 flex items-center justify-center text-xs text-slate-400">No Image</div>')
    display_image.short_description = 'Product Image'

@admin.register(Variation)
class VariationAdmin(ModelAdmin):
    list_display = ['item', 'category', 'title', 'price_modifier', 'active']
    list_filter = ['category', 'active', 'item__category']
    search_fields = ['title', 'item__title']

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(ModelAdmin):
    list_display = ['site_name', 'contact_email', 'contact_phone', 'shipping_cost', 'maintenance_mode']
    
    fieldsets = (
        ('Branding & SEO Settings', {
            'fields': ('site_name', 'site_logo', 'site_favicon', 'meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address'),
            'classes': ('collapse',),
        }),
        ('Pricing & E-commerce Rules', {
            'fields': ('currency_symbol', 'shipping_cost', 'free_shipping_threshold', 'tax_rate_percentage'),
            'classes': ('collapse',),
        }),
        ('Banners & Footer Content', {
            'fields': ('show_promo_banner', 'promo_banner_text', 'footer_about_text', 'footer_copyright_text'),
            'classes': ('collapse',),
        }),
        ('Social Media Links', {
            'fields': ('facebook_link', 'instagram_link', 'youtube_link', 'twitter_link'),
            'classes': ('collapse',),
        }),
        ('System Settings & Analytics', {
            'fields': ('google_analytics_id', 'maintenance_mode'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        # Allow adding only if there's no configuration yet
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of configuration settings
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        from django.urls import reverse
        
        # Get the first config instance
        config = SiteConfiguration.objects.first()
        if config:
            # Open edit form directly
            return redirect(reverse('admin:products_siteconfiguration_change', args=[config.pk]))
        # Open add form if no config row exists yet
        return redirect(reverse('admin:products_siteconfiguration_add'))

@admin.register(Wishlist)
class WishlistAdmin(ModelAdmin):
    list_display = ['user', 'session_key', 'item', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key', 'item__title']


@admin.register(PromoBanner)
class PromoBannerAdmin(ModelAdmin):
    list_display = ['display_image', 'title', 'section', 'tag', 'order', 'is_active']
    list_filter = ['section', 'is_active']
    search_fields = ['title', 'tag', 'description']
    list_editable = ['order', 'is_active']

    fieldsets = (
        ('Banner Information', {
            'fields': ('section', 'title', 'tag', 'description', 'image', 'icon_class', 'link_url', 'background_style', 'is_active', 'order')
        }),
        ('SEO & Accessibility', {
            'fields': ('image_alt', 'link_title', 'seo_rel_attribute'),
            'classes': ('collapse',),
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" class="w-12 h-12 rounded object-cover border border-slate-200 dark:border-zinc-800 shadow-sm" />')
        if obj.icon_class:
            return mark_safe(f'<div class="w-12 h-12 rounded bg-slate-100 dark:bg-zinc-800 flex items-center justify-center text-slate-500 text-lg"><i class="{obj.icon_class}"></i></div>')
        return mark_safe('<div class="w-12 h-12 rounded bg-slate-100 dark:bg-zinc-800 flex items-center justify-center text-xs text-slate-400">None</div>')
    display_image.short_description = 'Banner Preview'



