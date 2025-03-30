from django.shortcuts import render, get_object_or_404
from . models import Cart, CartItem
from products.models import Item
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def view(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, active=True)[0]
        except:
            cart = None
    else:
        try:
            the_id = request.session['cart_id']
            cart = Cart.objects.get(id=the_id)
        except:
            cart = None

    template = 'cart/cart_list.html'

    if cart:
        for item in cart.cartitem_set.all():
            if item.item.quantity == 0:
                item.active = False
                item.save()
            elif item.quantity > item.item.quantity:
                item.quantity = item.item.quantity
                item.active = False
                item.save()
                messages.warning(request,'Quantity of product has been compromised due \
                to unsufficient products. Please check')


        if cart.cartitem_set.count() < 1:
            empty_message = "Your cart is empty. Keep shoping."
            context = {"empty":True,"empty_message":empty_message}
            return render(request, template, context)
        l = len(CartItem.objects.filter(cart=cart, active=True))
        context = {"cart":cart,"len":l}
    else:
        context = {"empty":True}
    return render(request, template, context)

@login_required
def buy_now(request, slug):
    cart = Cart.objects.create(user=request.user, buy_now=True)
    item = get_object_or_404(Item, slug=slug)
    cart_item = CartItem.objects.create(cart=cart, item=item)
    qty = 1
    cart_item.quantity = int(qty)
    if item.discount_price:
        cart_item.line_total = Decimal(item.discount_price * int(qty))
    else:
        cart_item.line_total = Decimal(item.price * int(qty))
    cart.total = Decimal(cart.total)
    cart.total += cart_item.line_total
    cart.save()
    cart_item.save()
    return HttpResponseRedirect(reverse('products:checkout'))

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    if item.quantity == 0:
        messages.warning(request,'The product is out of stock')
        return HttpResponseRedirect(reverse('products:product',args=(slug,)))

    qty = int(request.POST.get('qty'))
    if qty > 0:
        if qty > 4:
            print('ds')
            messages.warning(request,'Can\'t order more than 4 items at a time')
            return HttpResponseRedirect(reverse('products:product',args=(slug,)))

        if qty > item.quantity:
            qty = item.quantity
            messages.warning(request, f'only {qty} item(s) left')
            return HttpResponseRedirect(reverse('products:product',args=(slug,)))
    else:
        messages.warning(request, f'Invalid quantity')
        return HttpResponseRedirect(reverse('products:product',args=(slug,)))

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, active=True)[0]
        except:
            cart = Cart.objects.create(user=request.user)

    else:
        try:
            the_id = request.session['cart_id']
        except:
            new_cart = Cart()
            new_cart.save()
            request.session['cart_id'] = new_cart.id
            the_id = new_cart.id
        cart = Cart.objects.get(id=the_id)

    cart_item, created = CartItem.objects.get_or_create(cart = cart, item = item)
    cart_item.quantity = qty
    if item.discount_price:
        cart_item.line_total = Decimal(item.discount_price * int(qty))
    else:
        cart_item.line_total = Decimal(item.price * int(qty))
    cart.total = Decimal(cart.total)
    cart.total += cart_item.line_total
    cart.save()
    cart_item.save()
    #    cart.items.add(cart_item)
    request.session['items_total'] = cart.cartitem_set.count()
    return HttpResponseRedirect(reverse('products:product',args=(slug,)))

def remove_from_cart(request, id):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, active=True)[0]
        except:
            return HttpResponseRedirect(reverse("cart:cart"))
    else:
        try:
            the_id = request.session['cart_id']
            cart = Cart.objects.get(id=the_id)
        except:
            return HttpResponseRedirect(reverse("cart:cart"))
    if cart.cartitem_set.count() < 1:
        empty_message = "Your cart is empty. Keep shoping."
        context = {"empty":True,"empty_message":empty_message}
        template = 'cart/cart_list.html'
        return render(request, template, context)
    #item = get_object_or_404(Item, slug = slug)
    cart_item = get_object_or_404(CartItem, id=id)
    cart.total -= cart_item.line_total
    cart.save()
    cart_item.cart = None
    cart_item.save()
        #cart_item.delete()
    request.session['items_total'] = cart.cartitem_set.count()
    print(request.session['items_total'])
    return HttpResponseRedirect(reverse("cart:cart"))

def active_cart_item(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    if item.item.quantity == 0:
        data = {
            'error': True
        }
        return JsonResponse(data)

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, active=True)[0]
        except:
            return HttpResponseRedirect(reverse("cart:cart"))

    else:
        try:
            the_id = request.session['cart_id']
            cart = Cart.objects.get(id=the_id)
        except:
            return HttpResponseRedirect(reverse("cart:cart"))

    item = get_object_or_404(CartItem, pk=pk)
    if item in cart.cartitem_set.all():
        if item.active == True:
            item.active = False
            cart.total -= item.line_total
        else:
            item.active = True
            cart.total += item.line_total
        item.save()
        cart.save()
        l = len(CartItem.objects.filter(cart=cart, active=True))
        data = {
            "msg": "updated",
            "active": item.active,
            "cart_total": cart.total,
            "len":l
        }
        return JsonResponse(data)
    else:
        raise PermissionDenied


def incri_item(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    if item.item.quantity == 0:
        messages.warning(request, 'Product is out of stock')
        return HttpResponseRedirect(reverse("cart:cart"))

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, active=True)[0]
        except:
            return HttpResponseRedirect(reverse("cart:cart"))
    else:
        try:
            the_id = request.session['cart_id']
            cart = Cart.objects.get(id=the_id)
        except:
            return HttpResponseRedirect(reverse("cart:cart"))

    if item in cart.cartitem_set.all():
        if item.quantity >= item.item.quantity:
            data = {
                'error':True
            }
            return JsonResponse(data)

        item.quantity += 1
        if item.item.discount_price:
            price = item.item.discount_price
        else:
            price = item.item.price
        if item.active:
            cart.total += price
        item.line_total += price
        item.save()
        cart.save()
        data = {
            'qty':item.quantity,
            'total':cart.total
        }
        return JsonResponse(data)
    else:
        raise PermissionDenied


def decri_item(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, active=True)[0]
        except:
            return HttpResponseRedirect(reverse("cart:cart"))
    else:
        try:
            the_id = request.session['cart_id']
            cart = Cart.objects.get(id=the_id)
        except:
            return HttpResponseRedirect(reverse("cart:cart"))
    if item in cart.cartitem_set.all():
        if item.quantity == 1:
            data = {
                'error':True
            }
            return JsonResponse(data)
        item.quantity -= 1
        if item.item.discount_price:
            price = item.item.discount_price
        else:
            price = item.item.price
        if item.active:
            cart.total -= price
        item.line_total -= price
        item.save()
        cart.save()
        item.save()
        data = {
            'qty':item.quantity,
            'total':cart.total
        }
        return JsonResponse(data)
    else:
        raise PermissionDenied
