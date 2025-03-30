from django.db import models
from products.models import Item
from django.conf import settings

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete = models.CASCADE, null = True, blank = True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    line_total = models.DecimalField(max_digits = 100, decimal_places=2, default = 00.00)
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    active = models.BooleanField(default = True)

    def __str__(self):
        try:
            return str(self.cart.id)
        except:
            return self.item.title

    def get_total_item_discount_price(self):
        return (self.quantity * (self.item.price - self.item.discount_price))

class Cart(models.Model):
#    items = models.ManyToManyField(CartItem, blank = True, null = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    total = models.DecimalField(max_digits = 100, decimal_places=2, default = 00.00)
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    active = models.BooleanField(default = True)

    def __str__(self):
        return f'Cart id is: {self.id}'
