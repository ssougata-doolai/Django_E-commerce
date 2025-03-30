from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from .forms import PhoneVerificationForm, OTPVerificationForm, Register
from .models import PhoneOTP
from django.urls import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.decorators import login_required
from orders.forms import CheckoutForm
from .models import UserAddress
from django.http import JsonResponse
from django import forms
from django.core.exceptions import PermissionDenied
from django.contrib import messages

import re
import random

def home(request):
    return render(request, 'accounts/home.html',{})

def send_otp(phone):
    otp = random.randint(99999,999999)
    print(otp)
    return otp



def validate_phone(request):
    form = PhoneVerificationForm()

    if request.method == 'POST':
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone_number')
            otp = send_otp(phone)
            obj, create = PhoneOTP.objects.get_or_create(phone_number = phone)
            obj.otp = otp
            request.session.create()
            obj.session = request.session.session_key
            obj.save()
            context = {
                'form': OTPVerificationForm(),
                'phone': phone
            }
#            data = {'phone': phone}
#            return JsonResponse(data)

        #     data = JsonResponse(dict(n_field_errors=list(p_form.non_field_errors)))
        #     return data
            return render(request, 'accounts/otp_verification.html', context)
            #return HttpResponseRedirect(reverse('verify-otp'))

    context = {
        'form': form
        }
    return render(request, 'accounts/phone_verification.html',context)

def validate_otp(request):
    try:
        obj = PhoneOTP.objects.get(session=request.session.session_key)
    except:
        return HttpResponseRedirect(reverse('accounts:verify-phone'))
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            if otp == obj.otp:
                obj.validate = True
                obj.save()
                return HttpResponseRedirect(reverse('accounts:register'))
            else:
#                data = {
#                    'status' : False,
#                    'msg' : 'Otp does\'t matched'
#                }
#                return JsonResponse(data)
                messages.warning(request,"Invalid OTP")
                return render(request, 'accounts/otp_verification.html', {'phone':obj.phone_number,'form':form})
        else:
            return render(request, 'accounts/otp_verification.html', {'phone':obj.phone_number,'form':form})

    else:
        form = OTPVerificationForm()
    return render(request, 'accounts/otp_verification.html',{'form':form})

def resend_otp(request):
    phone = request.GET.get('phone')
    try:
        obj = PhoneOTP.objects.get(phone_number=phone)
    except:
        form = OTPVerificationForm(request.POST)
        return render(request, 'accounts/otp_verification.html', {'phone':phone,'form':form})
    obj.otp = send_otp(phone)
    obj.save()

def register(request):
    try:
        obj = PhoneOTP.objects.get(session=request.session.session_key, validate=True)
    except:
        return HttpResponseRedirect(reverse('accounts:verify-phone'))
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            user = form.save()
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.phone_number = obj.phone_number
            user.save()
            obj.delete()
            request.session.create()
            return HttpResponseRedirect(reverse("accounts:login"))
    else:
        form = Register()
    return render(request, 'accounts/register.html',{'form':form})

SH1_RE = re.compile('^[a-f0-9]{40}$')

def activation_view(request, activation_key):
    if SH1_RE.search(activation_key):
        try:
            instance = EmailConfirmed.objects.get(activation_key = activation_key)
        except EmailConfirmed.DoesNotExist:
            instance = None
            raise Http404
        if instance and not instance.confirmed:
            instance.confirmed = True
            instance.save()
            page_message = "Activation Complete"
        elif instance and instance.confirmed:
            page_message = "Already Activated"
        else:
            page_message = ""

        context = {"page_message":page_message}
        return render(request, "accounts/activation_complete.html", context)
    else:
        raise Http404


@login_required
def add_address(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data.get('full_name')
#            last_name = request.POST.get('last_name')
            mobile_number = form.cleaned_data.get('mobile_number')
            street_address = form.cleaned_data.get('street_address')
            landmark = form.cleaned_data.get('landmark')
            city = form.cleaned_data.get('city')
            state = form.cleaned_data.get('state')
            zip = form.cleaned_data.get('zip')
            default = form.cleaned_data.get('default')
            user_address = UserAddress(
                user = request.user,
                full_name = full_name,
#                last_name = last_name,
                mobile_number = mobile_number,
                street_address = street_address,
                landmark = landmark,
                city = city,
                state = state,
                zip = zip,
#                default = default,
            )
            if default == 'on':
                for add in UserAddress.objects.filter(user = request.user):
                    add.default = False
                    add.save()
                user_address.default = True

            user_address.save()
            return redirect("products:checkout")
    else:
        form = CheckoutForm()
    context = {
        'form':form
    }
    return render(request, 'accounts/address.html', context)

@login_required
def update_address(request, pk):
    address = get_object_or_404(UserAddress, user=request.user, pk=pk)
#    if address in request.user.useraddress_set.all():
    if request.method == "POST":
        form = CheckoutForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('products:checkout')

    else:
        form = CheckoutForm(instance = address)
        context = {
            "form":form
        }
        return render(request, 'accounts/address.html', context)
    # else:
    #     raise PermissionDenied
