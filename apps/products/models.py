from django.db import models
from django.shortcuts import reverse

from django.conf import settings

LABEL_CHOICES = (
    ('S', 'sale'),
    ('N', 'new'),
    ('P', 'promotion')
)

class Slide(models.Model):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = models.ImageField(help_text='Size: 1920x570')
    is_active = models.BooleanField(default=True)
    image_alt = models.CharField(max_length=150, blank=True, null=True, help_text="Image alt tag for search engine indexing and accessibility.")

    def __str__(self):
        return f'{self.caption1} - {self.caption2}'

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')

    # SEO Fields
    seo_meta_title = models.CharField(max_length=70, blank=True, null=True, help_text="Custom meta title. Defaults to category title if blank.")
    seo_meta_description = models.TextField(blank=True, null=True, help_text="Custom meta description. Defaults to category description if blank.")
    seo_meta_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated SEO keywords.")
    image_alt = models.CharField(max_length=150, blank=True, null=True, help_text="Image alt tag for search engine indexing and accessibility.")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:category', kwargs={'slug': self.slug})

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    stock_no = models.CharField(max_length=10)
    description_short = models.CharField(max_length=50)
    description_long = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    # SEO Fields
    seo_meta_title = models.CharField(max_length=70, blank=True, null=True, help_text="Custom meta title. Defaults to product title if blank.")
    seo_meta_description = models.TextField(blank=True, null=True, help_text="Custom meta description. Defaults to product short description if blank.")
    seo_meta_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated SEO keywords.")
    seo_og_title = models.CharField(max_length=100, blank=True, null=True, help_text="Social media sharing (Open Graph) title.")
    seo_og_description = models.TextField(blank=True, null=True, help_text="Social media sharing (Open Graph) description.")
    seo_og_image = models.ImageField(upload_to='og_images/', blank=True, null=True, help_text="Social media sharing (Open Graph) image. Defaults to main product image if blank.")
    seo_schema_markup = models.TextField(blank=True, null=True, help_text="JSON-LD schema markup for structured search snippets.")

    def get_meta_title(self):
        return self.seo_meta_title or self.title

    def get_meta_description(self):
        return self.seo_meta_description or self.description_short

    def get_og_title(self):
        return self.seo_og_title or self.get_meta_title()

    def get_og_description(self):
        return self.seo_og_description or self.get_meta_description()

    def get_og_image_url(self):
        if self.seo_og_image:
            return self.seo_og_image.url
        elif self.image:
            return self.image.url
        return ""

    def has_sizes(self):
        return self.variations.filter(category='size', active=True).exists()

    def has_colors(self):
        return self.variations.filter(category='color', active=True).exists()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:product', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('cart:add-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('cart:remove-from-cart', kwargs={'slug': self.slug})

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'item'),)

    def __str__(self):
        return f"{self.user or self.session_key} - {self.item.title}"


class Variation(models.Model):
    VARIATION_CATEGORY_CHOICES = (
        ('color', 'color'),
        ('size', 'size'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='variations')
    category = models.CharField(max_length=120, choices=VARIATION_CATEGORY_CHOICES, default='size')
    title = models.CharField(max_length=120)
    price_modifier = models.FloatField(default=0.0, help_text="Additional price for this variation (optional)")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item.title} - {self.category.capitalize()}: {self.title}"


class SiteConfiguration(models.Model):
    # General & Branding
    site_name = models.CharField(max_length=255, default="Django E-commerce")
    site_logo = models.ImageField(upload_to="site_config/", blank=True, null=True, help_text="Upload website logo")
    site_favicon = models.ImageField(upload_to="site_config/", blank=True, null=True, help_text="Upload website favicon")
    meta_title = models.CharField(max_length=255, default="Best E-commerce Store", help_text="SEO Title")
    meta_description = models.TextField(blank=True, null=True, help_text="SEO Meta Description")

    # Contact & Store Location
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # E-commerce Rules
    currency_symbol = models.CharField(max_length=10, default="৳")
    shipping_cost = models.FloatField(default=60.0, help_text="Default shipping fee")
    free_shipping_threshold = models.FloatField(default=2000.0, help_text="Free shipping on orders above this amount")
    tax_rate_percentage = models.FloatField(default=0.0, help_text="Tax rate in percentage")

    # Banner & Footer settings
    show_promo_banner = models.BooleanField(default=True, help_text="Show promo bar at the top of site")
    promo_banner_text = models.CharField(max_length=255, default="Special Discount! Use code WELCOME10 for 10% off.", blank=True, null=True)
    footer_about_text = models.TextField(blank=True, null=True, help_text="About text in footer description")
    footer_copyright_text = models.CharField(max_length=255, default="© 2026 Django E-commerce. All rights reserved.")

    # Social Media URLs
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)

    # Analytics & Mode
    google_analytics_id = models.CharField(max_length=100, blank=True, null=True, help_text="Google Analytics G-XXXXXX ID")
    maintenance_mode = models.BooleanField(default=False, help_text="Enable to put site in Maintenance Mode")

    class Meta:
        verbose_name = "Website Configuration"
        verbose_name_plural = "Website Configurations"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton pattern - force overwrite of row 1
        super().save(*args, **kwargs)


class PromoBanner(models.Model):
    SECTION_CHOICES = (
        ('secondary_banner', 'Secondary Top Banner (Stack of 2 next to Hero)'),
        ('model_banner', 'Model Banner (Grid under Hero)'),
        ('gadget_feature', 'Gadget Feature Banner (Grid of 3)'),
        ('promo_block', 'Promo Block Banner (Grid of 2)'),
        ('special_banner', 'Special Banner (Widescreen bottom grid)'),
    )
    section = models.CharField(max_length=50, choices=SECTION_CHOICES)
    title = models.CharField(max_length=100)
    tag = models.CharField(max_length=100, blank=True, null=True, help_text="Small tagline or badge text")
    description = models.TextField(blank=True, null=True, help_text="Description or subtitle")
    image = models.ImageField(upload_to="banners/", blank=True, null=True)
    icon_class = models.CharField(max_length=100, blank=True, null=True, help_text="FontAwesome icon class (e.g. fas fa-credit-card)")
    link_url = models.CharField(max_length=255, default="/shop/", help_text="Target URL or link")
    background_style = models.CharField(max_length=255, blank=True, null=True, help_text="CSS background style (e.g. linear-gradient(135deg, #1e1b4b, #312e81))")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    # SEO Fields
    image_alt = models.CharField(max_length=150, blank=True, null=True, help_text="Image alt tag for search engine indexing and accessibility.")
    link_title = models.CharField(max_length=150, blank=True, null=True, help_text="Link title attribute for search engines.")
    seo_rel_attribute = models.CharField(max_length=50, blank=True, null=True, default="noopener noreferrer", help_text="Link rel attribute (e.g. 'nofollow', 'noopener noreferrer').")

    class Meta:
        verbose_name = "Promotional Banner"
        verbose_name_plural = "Promotional Banners"
        ordering = ['order', 'id']

    def __str__(self):
        return f"[{self.get_section_display()}] {self.title}"


class ItemMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    file = models.FileField(upload_to='product_media/', blank=True, null=True, help_text="Upload product image or video file (MP4 format).")
    video_url = models.URLField(blank=True, null=True, help_text="Or paste external video link (e.g. YouTube/Vimeo).")
    thumbnail = models.ImageField(upload_to='product_media/thumbnails/', blank=True, null=True, help_text="Thumbnail image (strongly recommended for video files).")
    image_alt = models.CharField(max_length=150, blank=True, null=True, help_text="SEO alt text for accessibility and search indexing.")
    order = models.IntegerField(default=0, help_text="Display order.")

    class Meta:
        verbose_name = "Product Media"
        verbose_name_plural = "Product Gallery Media"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.item.title} - {self.get_media_type_display()} ({self.id})"

    def get_youtube_id(self):
        if self.video_url:
            import re
            reg = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
            match = re.search(reg, self.video_url)
            if match:
                return match.group(1)
        return None

    def get_thumbnail_url(self):
        if self.media_type == 'image':
            return self.file.url if self.file else ""
        else:
            if self.thumbnail:
                return self.thumbnail.url
            yt_id = self.get_youtube_id()
            if yt_id:
                return f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
            return "/static/images/icons/video-16-9.jpg"




