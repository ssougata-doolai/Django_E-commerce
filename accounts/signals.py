from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from cart.models import Cart, CartItem
from accounts.models import EmailConfirmed
import random
import hashlib
from decimal import Decimal
from django.conf import settings


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def user_created(sender, instance, created, **kwargs):
#     if created:
#         email_confirmed, is_created = EmailConfirmed.objects.get_or_create(user = instance)
#         if is_created:
#             short_hash = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
#             username, domain = str(instance.email).split("@")
#             activation_key = hashlib.sha1((short_hash+username).encode('utf-8')).hexdigest()
#             email_confirmed.activation_key = activation_key
#             email_confirmed.save()
#             email_confirmed.activate_user_email()


@receiver(user_logged_in)
def move_to_user_cart(request, sender, user, **kwargs):
    print("in signal")
    try:
        the_id = request.session['cart_id']
        cart = Cart.objects.get(id=the_id)
    except:
        the_id = None
    if the_id:
        print("items no:",cart.cartitem_set.count())
        if cart.cartitem_set.count() > 0:
            try:
                new_cart = Cart.objects.filter(user = user, active=True)[0]
            except:
                new_cart = Cart.objects.create(user=user)

            #if created:
            #    new_cart.user = user
            #    new_cart.save()
            new_cart.total = Decimal(new_cart.total)
            for cart_item in cart.cartitem_set.all():
                try:
                    obj = CartItem.objects.get(cart=new_cart, item=cart_item.item)
                    new_cart.total -= obj.line_total
                    new_cart.total += cart_item.line_total
                    obj.quantity = cart_item.quantity

                except:

                    obj = cart_item
                    obj.cart = new_cart
                    new_cart.total += obj.line_total
                new_cart.save()
                obj.save()
            cart.delete()
    try:
        new_cart = Cart.objects.filter(user = user, active=True)[0]
        request.session['items_total'] = new_cart.cartitem_set.count()
    except:
        pass
