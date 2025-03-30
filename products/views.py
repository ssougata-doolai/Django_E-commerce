from django.shortcuts import render
from . models import Item
from .forms import ChooseQuantity
from cart.models import Cart, CartItem
from django.views.generic import (
    ListView,
    DetailView
)

class HomeView(ListView):
    model = Item
    template_name = "products/home.html"
    paginate_by = 8

    def get_queryset(self):
        return Item.objects.filter(active=True).order_by('-updated')

class ItemDetailView(DetailView):
    model = Item
    template_name = "products/product.html"

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView,self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                cart = Cart.objects.filter(user=self.request.user, active=True)[0]
            except:
                cart = None
        else:
            try:
                the_id = self.request.session['cart_id']
                cart = Cart.objects.get(id=the_id)
            except:
                cart = None

        context['cart_value'] = False
        if cart:
            cart_item = CartItem(cart = cart, item = self.object)
#            cart_item_filter = cart.cartitem_set.filter(item = self.object)
            if cart.cartitem_set.filter(item = self.object):
                context['cart_value'] = True
        context['form'] = ChooseQuantity()
        return context

def products(request):
    return render(request, 'products/product.html',{})
