import re
from django import forms
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('COD', 'Cash on Delivery (ক্যাশ অন ডেলিভারি)'),
    ('MFS', 'bKash / Nagad / Rocket (মোবাইল ব্যাংকিং)'),
    ('S', 'Credit / Debit Card (Stripe)')
)

DISTRICT_CHOICES = (
    ('Dhaka', 'Dhaka'),
    ('Chattogram', 'Chattogram'),
    ('Sylhet', 'Sylhet'),
    ('Khulna', 'Khulna'),
    ('Rajshahi', 'Rajshahi'),
    ('Barishal', 'Barishal'),
    ('Rangpur', 'Rangpur'),
    ('Mymensingh', 'Mymensingh'),
)

def validate_bangladeshi_phone(value):
    pattern = r'^(?:\+8801|01)[3-9]\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError("Please enter a valid Bangladeshi mobile number (e.g. 01712345678).")

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'House #, Road #, Area',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Flat, Floor (optional)',
        'class': 'form-control'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        }),
        initial='BD'
    )
    district = forms.ChoiceField(
        choices=DISTRICT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'custom-select d-block w-100'
        }),
        label="District/Division"
    )
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. 1207'
    }))
    phone_number = forms.CharField(
        validators=[validate_bangladeshi_phone],
        widget=forms.TextInput(attrs={
            'placeholder': '01XXXXXXXXX',
            'class': 'form-control'
        }),
        label="Mobile Number"
    )
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()
