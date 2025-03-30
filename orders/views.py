from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.views.generic import View
from django.contrib import messages
from . models import Order, CancelledOrder, TrackOrder
from cart.models import Cart
from . utils import id_generator, render_to_pdf
from django.contrib.auth.decorators import login_required
from accounts.models import UserAddress
from django.core.exceptions import PermissionDenied
from .forms import PaymentForm
from django.contrib import messages
from django.views.decorators.debug import sensitive_post_parameters
from decimal import Decimal
from django.template.loader import get_template
from .forms import OrderCancelForm
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token, csrf_protect
from PayTm import Checksum
import time
import requests
import json

@login_required
def checkout(request):
    try:
        cart = Cart.objects.filter(user=request.user, active=True)[0]
    except:
        cart = None
        return HttpResponseRedirect(reverse("cart:cart"))

    flag = False
    for item in cart.cartitem_set.all():
        if item.active == True:
            flag = True
            break

    if flag == False:
        messages.success(request,f'No cart item is selected !!')
        return HttpResponseRedirect(reverse("cart:cart"))

#    try:
    addresses = UserAddress.objects.filter(user = request.user)
#    except:
#        addresses = None
#        return HttpResponseRedirect(reverse("accounts:add-address"))

    if addresses.count() == 0:
        return HttpResponseRedirect(reverse("accounts:add-address"))
    addresses.update(active=False)
    default = False
    for address in addresses:
        if address.default == True:
            default = True
            break

    context = {
#        'form':form,
        'addresses':addresses,
        'default':default,
        'cart':cart
#        'order':new_order,
#        'items':new_order.cartitem_set
    }
    return render(request, 'products/checkout2.html', context)

@login_required
def set_address(request, pk):
    try:
        address = UserAddress.objects.get(pk=pk)
    except UserAddress.DoesNotExist:
        return HttpResponseRedirect(reverse("products:checkout"))

    if address in request.user.useraddress_set.all():
        request.user.useraddress_set.all().update(active=False)
        address.active = True
        address.save()
        data = {
            'active': address.active
        }
        return JsonResponse(data)
    else:
        raise PermissionDenied

@login_required
def place_order(request):

    if request.method == "POST":
        try:
            cart = Cart.objects.filter(user=request.user, active=True)[0]
        except:
            cart = None
            return HttpResponseRedirect(reverse("cart:cart"))

        address = None
        try:
            address = UserAddress.objects.get(user=request.user, active=True)
        except:
            try:
                address = UserAddress.objects.get(user=request.user, default=True)
            except:
                pass

        if not address:
            messages.success(request,f'No address is selected is selected !!')
            return HttpResponseRedirect(reverse("products:checkout"))

        new_cart = Cart.objects.create(user=request.user)
        for item in cart.cartitem_set.all():
            if not item.active:
                item.cart = new_cart
                item.save()
            else:
                request.session['items_total'] -= 1
        cart.active = False
        cart.save()
        try:
            new_order = Order.objects.get(cart = cart)
        except Order.DoesNotExist:
            new_order = Order()
            new_order.cart = cart
            new_order.user = request.user
            new_order.order_id = id_generator()
            new_order.line_total = cart.total
            new_order.tax_total = cart.total * Decimal(0.05)
            new_order.final_total = cart.total * Decimal(1.05)
            new_order.status = "Abandoned"
            try:
                address = UserAddress.objects.get(user=request.user, active=True)
            except:
                address = UserAddress.objects.get(user=request.user, default=True)
            new_order.full_name = address.full_name
            new_order.mobile_number = address.mobile_number
#            new_order.last_name = address.last_name
            new_order.street_address = address.street_address
            new_order.landmark = address.landmark
            new_order.city = address.city
            new_order.state = address.state
            new_order.zip = address.zip
#            new_order.status = "Finished"
            new_order.payment_status = 'Started'
            new_order.save()
            request.session['items_total'] = new_cart.cartitem_set.count()
            #request.session['items_total'].delete()
        except:
            return HttpResponseRedirect(reverse("cart:cart"))

        #return HttpResponseRedirect(reverse("orders:payment", args=(new_order.order_id)))
        form = PaymentForm()
        context = {'form':form, 'order_id':new_order.order_id}
        return render(request,'orders/payment.html',context)
    else:
        return HttpResponseRedirect(reverse("products:checkout"))

@login_required
# @sensitive_post_parameters('order_id')
def payment(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    if order.status == "Finished":
        messages.success(request, f'Order has been already places')
        return HttpResponseRedirect(reverse('orders:details', args=(order.order_id,)))
    order_id = order.order_id
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_option = form.cleaned_data.get('choice')
            if payment_option == "onDelevery":
                order.status = "Finished"
                order.payment_status = "Started"
                order.payment_method = "Cash on Delevery"
                order.updated_date = timezone.now()
                order.save()
                for item in order.cart.cartitem_set.all():
                    item.item.quantity -= item.quantity
                    item.item.save()
                messages.success(request,f'Order succesfully placed')
                return HttpResponseRedirect(reverse('orders:details', args=(order_id,)))
            else:
                # url = reverse('orders:handle-request')
                # param_dict = {
                #     'MID':'RRmIzm20000872252787',
                #     'ORDER_ID':str(order.order_id),
                #     'TXN_AMOUNT':str(order.final_total),
                #     'CUST_ID':str(request.user.id),
                #     'INDUSTRY_TYPE_ID':'Retail',
                #     'WEBSITE':'WEBSTAGING',
                #     'CHANNEL_ID':'WEB',
                #     'CALLBACK_URL':'http://127.0.0.1:8000'+reverse('orders:handle-request'),
                # }
                # param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, "sxYr2nX!c9kYs7PI")
                # return render(request, 'orders/paytm.html', {'param_dict':param_dict})
                # initialize a dictionary
                paytmParams = dict()
                # body parameters
                paytmParams["body"] = {
                    # for custom checkout value is 'Payment' and for intelligent router is 'UNI_PAY'
                    "requestType" : "Payment",
                    # Find your MID in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
                    "mid" : "RRmIzm20000872252787",
                    # Find your Website Name in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
                    "websiteName" : "WEBSTAGING",
                    # Enter your unique order id
                    "orderId" : str(order.order_id),
                    # on completion of transaction, we will send you the response on this URL
                    "callbackUrl" : 'http://127.0.0.1:8000/order/payment/handleRequest/',
                    # Order Transaction Amount here
                    "txnAmount" : {
                        # Transaction Amount Value
                        "value" : str(order.final_total),
                        # Transaction Amount Currency
                        "currency" : "INR",
                    },
                    # Customer Infomation here
                    "userInfo" : {
                        # unique id that belongs to your customer
                        "custId" : str(request.user.phone_number),
                    },
                }
                # Generate checksum by parameters we have in body
                # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
                checksum = Checksum.generate_checksum_by_str(json.dumps(paytmParams["body"]), "sxYr2nX!c9kYs7PI")
                # head parameters
                paytmParams["head"] = {
                    # put generated checksum value here
                    "signature"	: checksum
                }
                # prepare JSON string for request
                post_data = json.dumps(paytmParams)
                # for Staging
                url = f"https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid=RRmIzm20000872252787&orderId={order.order_id}"
                # for Production
                # url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=YOUR_ORDER_ID"
                response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
                return HttpResponseRedirect(reverse('orders:handle-request', args=(order_id, response['body']['txnToken'],)))
            return render(request, 'orders/payment.html', {'form':form,'order_id':order_id})
    else:
        form = PaymentForm()
    return render(request, 'orders/payment.html', {'form':form, 'order_id':order_id})


def handle_payment_request(request, order_id, txnToken):
    # initialize a dictionary
    paytmParams = dict()

    # head parameters
    paytmParams["head"] = {

        # put transaction token here, this is same token which was generated by Initiate Transaction API
        "txnToken" : str(txnToken)
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    # for Staging
    url = f"https://securegw-stage.paytm.in/fetchPaymentOptions?mid=RRmIzm20000872252787&orderId={order_id}"

    # for Production
    # url = "https://securegw.paytm.in/fetchPaymentOptions?mid=YOUR_MID_HERE&orderId=YOUR_ORDER_ID"

    response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
    #return HttpResponse(response)
    return render(request, 'payment/payment_response.html', {})

@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    return render(request, 'orders/order_details.html',{'order':order})

@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    if order.status == "Finished":
        return render(request, 'orders/order_summary.html', {'order':order})
    else:
        return HttpResponseRedirect(reverse('orders:view-order-all'))

@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    if order.status == "Finished":
        pdf = render_to_pdf('orders/invoice.html',{'order':order})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f"Invoice_{order.order_id}.pdf"
            print(filename)
            content = f"inline; filename={filename}"
            download = request.GET.get("download")
            if download:
                content = f"attachment; filename={filename}"
            response['Content-Disposition'] = content
            return response

    else:
        return HttpResponseRedirect(reverse('orders:view-order-all'))


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    if order.status == 'Canceled':
        ref = reverse('orders:details', kwargs={'order_id':order.order_id})
        messages.warning(request,f'Order <a href="{ref}">#{order.order_id}</a> is already cancelled')
        return HttpResponseRedirect(reverse('orders:view-order-all'))
    elif order.shipping_status == 'Arrived':
        messages.warning(request,'Order has been already received')
        return HttpResponseRedirect(reverse('orders:view-order-all'))
    if request.method == 'POST':
        form = OrderCancelForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('reason')
            other_reason = form.cleaned_data.get('other_reason')
            print(other_reason)
            if reason == 'Other' and other_reason == '':
                messages.warning(request, 'Please describe the other reason')
#                print(form.fields['other_reason'].value)
            else:
                messages.warning(request, 'Order is cancelled')
                CancelledOrder.objects.create(order=order, reason=reason, other_reason=other_reason)
                order.status = 'Canceled'
                order.save()
                return HttpResponseRedirect(reverse('orders:view-order-all'))
    else:
        form = OrderCancelForm()
    return render(request, 'orders/cancel_order.html',{'form':form,'order_id':order.order_id})

@login_required
def view_order(request):
    try:
        orders = Order.objects.filter(user = request.user).order_by('-created_date')
    except:
        orders = None
    context = {
        'orders':orders
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def shipped_order(request):
    try:
        orders = Order.objects.filter(user=request.user, shipping_status="Arrived").order_by('-created_date')
    except:
        orders = None
    context = {
        'orders':orders
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    track_details = TrackOrder.objects.filter(order=order)
    return render(request, 'orders/track_order.html', {'track_details':track_details,'order':order})

# class CheckoutView(View):
#     def get(self, *args, **kwargs):
#         form = CheckoutForm()
#         try:
#             the_id = self.request.session['cart_id']
#             cart = Cart.objects.get(id=the_id)
#         except:
#             the_id = None
#             return HttpResponseRedirect(reverse("cart:cart"))
#         new_order, created = Order.objects.get_or_create(cart=cart)
#         if created:
#             new_order.order_id = str(time.time())
#             new_order.save()
#         context = {"form":form}
#         return render(self.request, 'products/checkout.html',context)
#
#     def post(self, *args, **kwargs):
#         form = CheckoutForm(self.request.POST or None)
#         try:
#             the_id = self.request.session['cart_id']
#             cart = Cart.objects.get(id=the_id)
#         except:
#             the_id = None
#             return HttpResponseRedirect(reverse("cart:cart"))
#         new_order, created = Order.objects.get_or_create(cart=cart)
#         if created:
#             new_order.order_id = str(time.time())
#             new_order.save()
#         if form.is_valid():
#             print("Form is valid")
#             if new_order.status == "Finished":
#                 del self.request.session['cart_id']
#                 del self.request.session['items_total']
#             return redirect("products:checkout")
#         print("Falied")
#         messages.warning(self.request,"Failed checkout")
#         return redirect("products:checkout")
#         #context = {"form":form}
#         #return render(request, 'products/checkout.html',context)
