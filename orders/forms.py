from django import forms
from django.http import JsonResponse
from accounts.models import UserAddress

from . models import CancelledOrder

PAYMENT_CHOICES = (
    ('Stripe','Stripe'),
    ('Paypal','Paypal'),
    ('onDelevery','Cash on Delevery'),
)

CANCEL_REASON = (
    ('Delay','The delivery is delayed'),
    ('Mistake','Order placed by mistake'),
    ('High Cost','Item price/shipping cost is too high'),
    ('Change','Need to change shipping address'),
    ('Bought','Bought it from somewhere else'),
    ('Problem','Have problem with payment'),
    ('Other','My reason is not listed'),
)

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['full_name','mobile_number','street_address','landmark','city','state','zip','default']

    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.errors:
                visible.field.widget.attrs['class'] = 'form-control is-invalid'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

class PaymentForm(forms.Form):
    choice = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect)

    #CharField(widget=forms.RadioSelect(choices=PAYMENT_CHOICES))
    #ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect)

class OrderCancelForm(forms.ModelForm):
    reason = forms.ChoiceField(choices=CANCEL_REASON, widget=forms.RadioSelect)
    class Meta:
        model = CancelledOrder
        fields = ('reason','other_reason',)
