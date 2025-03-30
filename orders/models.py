from django.db import models
from cart.models import Cart
from django.conf import settings
from django.core.validators import RegexValidator
#from decimal import Decimal

STATUS_CHOICES = (
    ("Started","Started"),
    ("Abandoned","Abandoned"),
    ("Finished","Finished"),
    ("Canceled","Canceled"),
)

PAYMENT_CHOICE = (
    ("Started","Started"),
    ("Finished","Finished"),
)

SHIPPING_CHOICE = (
    ("Shipped","Shipped"),
    ("Out","Out for delevery"),
    ("Arrived","Arrived"),
)

PAYMENT_METHODS = (
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

phone_regex = RegexValidator(regex = r'^\+?1?\d{9,14}$',
message = "Phone number is not valid.")
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=120, default="ABc", unique =True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    line_total = models.DecimalField(max_digits = 100, decimal_places=2, default = 0.00)
    tax_total = models.DecimalField(max_digits = 100, decimal_places=2, default = 5.99)
    final_total = models.DecimalField(max_digits = 100, decimal_places=2, default = 19.99)
    status = models.CharField(max_length = 40, choices = STATUS_CHOICES, default="Started")
    payment_status = models.CharField(max_length=10, choices = PAYMENT_CHOICE, blank=True, null=True)
    payment_method = models.CharField(max_length=30, choices = PAYMENT_METHODS, blank=True, null=True)
    shipping_status = models.CharField(max_length=10, choices = SHIPPING_CHOICE, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    full_name = models.CharField(max_length=60)
    mobile_number = models.CharField(validators = [phone_regex], max_length = 15)
    street_address = models.CharField(max_length=120)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10)

    def __str__(self):
        return self.order_id

class CancelledOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.CharField(max_length=55, choices = CANCEL_REASON)
    other_reason = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.reason

class TrackOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    location = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.order.user.phone_number
