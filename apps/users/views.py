from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import UserForm, UserProfileForm
from apps.orders.models import Order
from .models import UserProfile
from apps.cart.views import get_active_cart
from apps.products.views import get_wishlist_queryset

class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        orders = Order.objects.filter(user=request.user, ordered=True).order_by('-id')
        active_cart = get_active_cart(request)
        wishlist_items = get_wishlist_queryset(request)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'orders': orders,
            'profile': profile,
            'active_cart': active_cart,
            'wishlist_items': wishlist_items
        }
        return render(request, 'profile.html', context)

    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        orders = Order.objects.filter(user=request.user, ordered=True).order_by('-id')
        active_cart = get_active_cart(request)
        wishlist_items = get_wishlist_queryset(request)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile-detail')
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'orders': orders,
            'profile': profile,
            'active_cart': active_cart,
            'wishlist_items': wishlist_items
        }
        return render(request, 'profile.html', context)

class OrderHistoryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect('/users/profile/#orders')
