from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import PhoneOTP, UserAddress
#from .forms import UserAdminCreationForm, UserAdminChangeForm


class UserAdmin(BaseUserAdmin):
    #The form to add and change user instances
#    form = UserAdminChangeForm
#    add_form = UserAdminCreationForm

    #The fields to be used in displaying the User model.
    list_display = ('phone_number', 'name', 'admin',)
    list_filter = ('staff', 'active', 'admin',)
    ordering = ('phone_number','name',)
    filter_horizontal = ()

    fieldsets = (
        (None,{'fields':('phone_number','password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions',{'fields':('admin','staff','active')}),
    )

    add_fieldsets = (
        (None, {
            'classes':('wide'),
            'fields':('phone_number', 'password1', 'password2')
        }),
    )

#    def get_inline_instances(self, request, obj=None):
#        if not obj:
#            return list()
#        return super(UserAdmin, self).get_inline_instances(request, obj)

admin.site.register(User, UserAdmin)
admin.site.register(PhoneOTP)
admin.site.register(UserAddress)
