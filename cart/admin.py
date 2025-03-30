from django.contrib import admin
from . models import Cart, CartItem

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['item','quantity','created_date','line_total','active']
    class Meta:
        model = CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ['user','total']

    class Meta:
        model = Cart

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
