from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.generic import View
import random
import string
from .forms import CheckoutForm, CouponForm, RefundForm
from .models import Order, Coupon, Refund
from apps.users.models import BillingAddress
from apps.payments.models import Payment
from apps.cart.views import get_active_cart

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, 'This coupon does not exist')
        return redirect('orders:checkout')

class CheckoutView(View):
    def get(self, *args, **kwargs):
        order = get_active_cart(self.request)
        if order:
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, 'checkout.html', context)
        else:
            messages.info(self.request, 'You do not have an active order')
            return redirect('cart:order-summary')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        order = get_active_cart(self.request)
        if not order:
            messages.error(self.request, 'You do not have an active order')
            return redirect('cart:order-summary')
            
        if form.is_valid():
            street_address = form.cleaned_data.get('street_address')
            apartment_address = form.cleaned_data.get('apartment_address')
            country = form.cleaned_data.get('country')
            district = form.cleaned_data.get('district')
            phone_number = form.cleaned_data.get('phone_number')
            zip = form.cleaned_data.get('zip')
            payment_option = form.cleaned_data.get('payment_option')

            billing_address = BillingAddress(
                user=self.request.user if self.request.user.is_authenticated else None,
                street_address=street_address,
                apartment_address=apartment_address,
                country=country,
                district=district,
                phone_number=phone_number,
                zip=zip,
                address_type='B'
            )
            billing_address.save()
            order.billing_address = billing_address
            order.save()

            if payment_option == 'COD':
                payment = Payment()
                payment.user = self.request.user if self.request.user.is_authenticated else None
                payment.amount = order.get_total()
                payment.payment_method = 'Cash on Delivery'
                payment.save()
                order.payment = payment
                order.ordered = True
                order.ref_code = create_ref_code()
                order.save()
                
                # Clear session cart ID if guest
                if not self.request.user.is_authenticated:
                    if 'order_id' in self.request.session:
                        del self.request.session['order_id']
                        
                messages.success(self.request, 'Your order has been successfully placed via Cash on Delivery!')
                return redirect('/')
            elif payment_option == 'MFS':
                return redirect('payments:payment', payment_option='mfs')
            elif payment_option == 'S':
                return redirect('payments:payment', payment_option='stripe')
            else:
                messages.warning(self.request, 'Invalid payment option selected')
                return redirect('orders:checkout')
        else:
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, 'checkout.html', context)

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            order = get_active_cart(self.request)
            if order:
                code = form.cleaned_data.get('code')
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, 'Successfully added coupon')
                return redirect('orders:checkout')
            else:
                messages.info(self.request, 'You do not have an active order')
                return redirect('orders:checkout')
        return redirect('orders:checkout')

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {'form': form}
        return render(self.request, 'request_refund.html', context)
        
    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                refund = Refund(order=order, reason=message, email=email)
                refund.save()
                messages.info(self.request, 'Your request was received')
                return redirect('orders:request-refund')
            except ObjectDoesNotExist:
                messages.info(self.request, 'This order does not exist')
                return redirect('orders:request-refund')
