import os
import requests
from django.core.files.base import ContentFile
from apps.products.models import PromoBanner

# Define banners data
banners_data = [
    # 1. Secondary Top Banners
    {
        'section': 'secondary_banner',
        'title': 'Travel Essentials',
        'tag': 'Hot Offers',
        'description': 'Gear up for the adventure. 38% OFF!',
        'image_url': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400',
        'order': 1
    },
    {
        'section': 'secondary_banner',
        'title': 'Kids & Baby Dolls',
        'tag': 'Sweet Toy',
        'description': 'Cute toys for kids. Up to 50% OFF!',
        'image_url': 'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400',
        'order': 2
    },
    # 2. Model Banners
    {
        'section': 'model_banner',
        'title': 'Premium Dresses',
        'tag': 'Fashion',
        'image_url': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=300',
        'order': 1
    },
    {
        'section': 'model_banner',
        'title': 'Cosmetics & Care',
        'tag': 'Beauty',
        'image_url': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=300',
        'order': 2
    },
    {
        'section': 'model_banner',
        'title': 'Urban Sneakers',
        'tag': 'Footwear',
        'image_url': 'https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=300',
        'order': 3
    },
    {
        'section': 'model_banner',
        'title': 'Travel Accessories',
        'tag': 'Lifestyle',
        'image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300',
        'order': 4
    },
    # 3. Gadget Feature Banners
    {
        'section': 'gadget_feature',
        'title': 'Tech Watch Collection',
        'tag': 'Smart Wear',
        'background_style': 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)',
        'order': 1
    },
    {
        'section': 'gadget_feature',
        'title': 'Premium Wireless Audio',
        'tag': 'Hi-Fi Audio',
        'background_style': 'linear-gradient(135deg, #064e3b 0%, #065f46 100%)',
        'order': 2
    },
    {
        'section': 'gadget_feature',
        'title': 'Everyday Gadget Kits',
        'tag': 'Essentials',
        'background_style': 'linear-gradient(135deg, #701a75 0%, #86198f 100%)',
        'order': 3
    },
    # 4. Promo Blocks
    {
        'section': 'promo_block',
        'title': 'Family Collection',
        'tag': 'Lifestyle',
        'image_url': 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=300',
        'order': 1
    },
    {
        'section': 'promo_block',
        'title': 'Tech Watch Hero',
        'tag': 'Wearables',
        'image_url': 'https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=300',
        'order': 2
    },
    {
        'section': 'promo_block',
        'title': 'FINELOOK SNEAKERS',
        'tag': 'Premium Brand',
        'order': 3
    },
    {
        'section': 'promo_block',
        'title': 'Leather Bags Hero',
        'tag': 'Bags',
        'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=300',
        'order': 4
    },
    # 5. Special Banners
    {
        'section': 'special_banner',
        'title': '10% Cash Back',
        'description': 'On select Visa/Mastercard payments.',
        'icon_class': 'fas fa-credit-card',
        'order': 1
    },
    {
        'section': 'special_banner',
        'title': 'Casual Lifestyle',
        'tag': 'Trending Model',
        'image_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300',
        'order': 2
    },
    {
        'section': 'special_banner',
        'title': 'Perfect Gift',
        'description': 'Get gift vouchers for friends and family.',
        'icon_class': 'fas fa-gift',
        'order': 3
    },
    {
        'section': 'special_banner',
        'title': 'Budget Deals',
        'description': 'Save massive amounts on bulk options.',
        'icon_class': 'fas fa-tags',
        'order': 4
    }
]

# Delete existing ones to avoid duplicates
PromoBanner.objects.all().delete()

for idx, item in enumerate(banners_data):
    banner = PromoBanner(
        section=item['section'],
        title=item['title'],
        tag=item.get('tag'),
        description=item.get('description'),
        icon_class=item.get('icon_class'),
        background_style=item.get('background_style'),
        order=item['order']
    )
    
    if item.get('image_url'):
        url = item['image_url']
        try:
            print(f"Downloading image for {item['title']}...")
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                filename = f"banner_{idx}.jpg"
                banner.image.save(filename, ContentFile(res.content), save=False)
        except Exception as e:
            print(f"Failed to download image from {url}: {e}")
            
    banner.save()
    print(f"Saved: {banner}")

print("All promotional banners loaded successfully!")
