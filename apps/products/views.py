from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.db.models import Q
from .models import Item, Category, Wishlist, PromoBanner

class HomeView(ListView):
    template_name = 'index.html'
    model = Item
    
    def get_queryset(self):
        return Item.objects.filter(is_active=True)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        
        # Load custom promotional banners dynamically
        banners = PromoBanner.objects.filter(is_active=True)
        context['secondary_banners'] = banners.filter(section='secondary_banner')
        context['model_banners'] = banners.filter(section='model_banner')
        context['gadget_features'] = banners.filter(section='gadget_feature')
        context['promo_blocks'] = banners.filter(section='promo_block')
        context['special_banners'] = banners.filter(section='special_banner')
        return context

class ShopView(ListView):
    model = Item
    template_name = 'shop.html'

    def get_queryset(self):
        queryset = Item.objects.filter(is_active=True)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description_long__icontains=q) |
                Q(description_short__icontains=q) |
                Q(category__title__icontains=q)
            )
        return queryset


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_products = Item.objects.filter(
            category=self.object.category, 
            is_active=True
        ).exclude(id=self.object.id)[:8]
        if related_products.count() < 4:
            additional_items = Item.objects.filter(is_active=True).exclude(id=self.object.id).exclude(category=self.object.category)[:8 - related_products.count()]
            related_products = list(related_products) + list(additional_items)
        context['related_products'] = related_products
        return context

class CategoryView(View):
    def get(self, *args, **kwargs):
        category = Category.objects.get(slug=self.kwargs['slug'])
        items = Item.objects.filter(category=category, is_active=True)
        context = {
            'object_list': items,
            'category_title': category,
            'category_description': category.description,
            'category_image': category.image
        }
        return render(self.request, 'category.html', context)


def category_list_api(request):
    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('title')
    data = []
    for cat in categories:
        subs = cat.subcategories.filter(is_active=True).order_by('title')
        subs_data = [{'title': sub.title, 'slug': sub.slug, 'url': sub.get_absolute_url()} for sub in subs]
        data.append({
            'title': cat.title,
            'slug': cat.slug,
            'url': cat.get_absolute_url(),
            'subcategories': subs_data
        })
    return JsonResponse({'categories': data})


def product_search_api(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    
    items = Item.objects.filter(is_active=True, title__icontains=query)[:8]
    
    results = []
    for item in items:
        results.append({
            'title': item.title,
            'url': item.get_absolute_url(),
            'price': f"৳{item.price:.2f}",
            'discount_price': f"৳{item.discount_price:.2f}" if item.discount_price else None,
            'image': item.image.url if item.image else ''
        })
        
    return JsonResponse({'results': results})


def get_wishlist_queryset(request):
    if request.user.is_authenticated:
        session_key = request.session.session_key
        if session_key:
            session_wishlist = Wishlist.objects.filter(session_key=session_key)
            for w_item in session_wishlist:
                if not Wishlist.objects.filter(user=request.user, item=w_item.item).exists():
                    w_item.user = request.user
                    w_item.session_key = None
                    w_item.save()
                else:
                    w_item.delete()
        return Wishlist.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(session_key=session_key)

def toggle_wishlist_ajax(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user, item=item)
        if wishlist_qs.exists():
            wishlist_qs.delete()
            status = 'removed'
        else:
            Wishlist.objects.create(user=request.user, item=item)
            status = 'added'
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        wishlist_qs = Wishlist.objects.filter(session_key=session_key, item=item)
        if wishlist_qs.exists():
            wishlist_qs.delete()
            status = 'removed'
        else:
            Wishlist.objects.create(session_key=session_key, item=item)
            status = 'added'
            
    updated_qs = get_wishlist_queryset(request)
    count = updated_qs.count()
    items_list = [w.item.slug for w in updated_qs]
    
    return JsonResponse({
        'status': status,
        'count': count,
        'items': items_list
    })

def wishlist_info_api(request):
    updated_qs = get_wishlist_queryset(request)
    count = updated_qs.count()
    items_list = [w.item.slug for w in updated_qs]
    
    return JsonResponse({
        'count': count,
        'items': items_list
    })

class WishlistSummaryView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/users/profile/#wishlist')
        wishlist_qs = get_wishlist_queryset(request)
        context = {
            'wishlist_items': wishlist_qs
        }
        return render(request, 'wishlist.html', context)

def auth_status_api(request):
    if request.user.is_authenticated:
        username = request.user.username or request.user.email or "User"
        links = [
            {'label': f"Hi, {username}!", 'url': '#', 'class': 'font-weight-bold text-primary'},
            {'label': 'My Profile', 'url': reverse('users:profile-detail'), 'class': ''},
            {'label': 'My Wishlist', 'url': reverse('users:profile-detail') + '#wishlist', 'class': ''},
            {'label': 'Order Summary', 'url': reverse('users:profile-detail') + '#cart', 'class': ''},
            {'label': 'Order History', 'url': reverse('users:profile-detail') + '#orders', 'class': ''},
            {'label': 'Logout', 'url': reverse('account_logout'), 'class': 'text-danger'}
        ]
        return JsonResponse({
            'is_authenticated': True,
            'username': username,
            'links': links
        })
    else:
        links = [
            {'label': 'Login', 'url': reverse('account_login'), 'class': 'font-weight-bold'},
            {'label': 'Sign Up', 'url': reverse('account_signup'), 'class': ''}
        ]
        return JsonResponse({
            'is_authenticated': False,
            'username': None,
            'links': links
        })

