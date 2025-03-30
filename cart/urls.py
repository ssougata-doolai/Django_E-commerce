from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('',views.view, name='cart'),
    path('<slug>/add/',views.add_to_cart, name='add-to-cart'),
    path('<id>/remove/',views.remove_from_cart, name='remove-from-cart'),
    path('<pk>/active/',views.active_cart_item, name='active_cart_item'),
    path('<pk>/increament-order-quantity/',views.incri_item, name='incri-item'),
    path('<pk>/decrement-order-quantity/',views.decri_item, name='decri-item'),
    path('<slug>/buy-now/',views.buy_now, name='buy-now'),
]
