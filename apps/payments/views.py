from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View
import stripe
from apps.orders.models import Order
from apps.orders.views import create_ref_code
from apps.cart.views import get_active_cart
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentView(View):
    def get(self, *args, **kwargs):
        payment_option = self.kwargs.get('payment_option')
        order = get_active_cart(self.request)
        if order:
            if order.billing_address:
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False,
                    'payment_option': payment_option,
                    'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
                }
                return render(self.request, 'payment.html', context)
            else:
                messages.warning(self.request, 'You have not added a billing address')
                return redirect('orders:checkout')
        else:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')

    def post(self, *args, **kwargs):
        payment_option = self.kwargs.get('payment_option')
        order = get_active_cart(self.request)
        if not order:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')
            
        if payment_option == 'mfs':
            mfs_provider = self.request.POST.get('mfs_provider', 'bKash')
            transaction_id = self.request.POST.get('transaction_id', '')
            sender_number = self.request.POST.get('sender_number', '')
            if not transaction_id or not sender_number:
                messages.error(self.request, 'Please enter your Mobile Number and Transaction ID.')
                return redirect('payments:payment', payment_option='mfs')
            
            payment = Payment(
                stripe_charge_id=transaction_id,
                payment_method=f'MFS ({mfs_provider}) - Sender: {sender_number}',
                user=self.request.user if self.request.user.is_authenticated else None,
                amount=order.get_total()
            )
            payment.save()
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            
            # Clear session cart ID if guest
            if not self.request.user.is_authenticated:
                if 'order_id' in self.request.session:
                    del self.request.session['order_id']
                    
            messages.success(self.request, f'Successfully placed order! Payment verification via {mfs_provider} is pending.')
            return redirect('/')
        elif payment_option == 'stripe':
            token = self.request.POST.get('stripeToken')
            amount = int(order.get_total() * 100)
            try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency='bdt',
                    source=token
                )
                payment = Payment(
                    stripe_charge_id=charge['id'],
                    payment_method='Stripe Card',
                    user=self.request.user if self.request.user.is_authenticated else None,
                    amount=order.get_total()
                )
                payment.save()
                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()
                
                # Clear session cart ID if guest
                if not self.request.user.is_authenticated:
                    if 'order_id' in self.request.session:
                        del self.request.session['order_id']
                        
                messages.success(self.request, 'Card payment was successful!')
                return redirect('/')
            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.error(self.request, f"{err.get('message')}")
                return redirect('/')
            except Exception as e:
                messages.error(self.request, f'An error occurred: {str(e)}')
                return redirect('/')
        else:
            messages.error(self.request, 'Invalid payment request')
            return redirect('orders:checkout')
