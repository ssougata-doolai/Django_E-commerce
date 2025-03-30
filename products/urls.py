from django.urls import path
from . views import (
    HomeView,
    ItemDetailView
)

from orders.views import checkout
app_name = 'products'

urlpatterns = [
    path('',HomeView.as_view(), name='home'),
    path('checkout/',checkout, name='checkout'),
    path('product/<slug>/',ItemDetailView.as_view(), name='product'),
]
