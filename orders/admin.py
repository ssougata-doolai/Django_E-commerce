from django.contrib import admin

from . models import Order, CancelledOrder, TrackOrder

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id','user','cart','final_total','city']
    class Meta:
        model = Order

admin.site.register(Order, OrderAdmin)
admin.site.register(CancelledOrder)
admin.site.register(TrackOrder)
