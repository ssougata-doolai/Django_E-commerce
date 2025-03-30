from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex = r'^\+?1?\d{9,14}$',
message = "Phone number is not valid.")

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, is_staff = False, is_active=True, is_admin=False):
        if not phone_number:
            raise ValueError('User must have a phone number')
        if not password:
            raise ValueError('User must have a passowrd')

        user_obj = self.model(
            phone_number = phone_number
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_stuffuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number,
            password = password,
            is_staff = True
        )
        return user

    def create_superuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number,
            password = password,
            is_staff = True,
            is_admin = True
        )
        return user

class User(AbstractBaseUser):
    phone_number = models.CharField(_('phone number'), validators = [phone_regex], max_length = 15, unique = True)
    name = models.CharField(max_length = 50)
    email = models.EmailField(null=True, blank=True)
    first_login = models.BooleanField(default = False)
    active = models.BooleanField(default = True)
    staff = models.BooleanField(default = False)
    admin = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add = True)

    USERNAME_FIELD = 'phone_number'
    REQUEIRED_FIELDS = []

    objetcs = UserManager()

    def __str__(self):
        return self.phone_number

    def get_full_name(self):
        if self.name:
            return self.name
        else:
            return self.phone_number

    def get_short_name(self):
        return self.phone_number

    def has_perm(self, prem, obj=None):
        return True

    def has_module_perms(self, app_lebel):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


otp_regex = RegexValidator(regex = r'^\+?1?\d{6,6}$', message = "Enter a valid otp")
class PhoneOTP(models.Model):
    phone_number = models.CharField(validators = [phone_regex], max_length = 15, unique = True)
    otp = models.CharField(validators = [otp_regex], max_length=6)
    count = models.IntegerField(default = 0)
    session = models.CharField(max_length = 50)
    validate = models.BooleanField(default=False)

    def __str__(self):
        return str(self.phone_number) + ' is sent ' + str(self.otp)

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

class EmailConfirmed(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length = 100)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.confirmed)

    def activate_user_email(self):
        subject = 'Activate your email'
        activation_url = "http://127.0.0.1:8000/accounts/activate/%s"%(self.activation_key)
        context = {
            "activation_key":self.activation_key,
            "activation_url":activation_url
        }
        message = render_to_string("accounts/activation_message.txt", context)
        self.email_to_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    def email_to_user(self, subject, message, from_mail=None, **kwargs):
        send_mail(subject, message, from_mail, [self.user.email,], fail_silently=False,)


class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    full_name = models.CharField(max_length=60)
    mobile_number = models.CharField(validators = [phone_regex], max_length = 15)
    street_address = models.CharField(max_length=120)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10)
    default = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.street_address + " " + self.city
