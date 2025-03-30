from django import forms
from .models import User, PhoneOTP
from django.contrib.auth.forms import AuthenticationForm

'''
class LoginForm(forms.Form):
    phone_number = forms.IntegerField(label='Your Phone Number')
    password = forms.CharField(widget = forms.PasswordInput)
'''

class AuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        #self.fields['username'] #= forms.CharField(label='dfds',widget=forms.TextInput(attrs={'id':'id_mobile_number'}), required=True)
        #
        #forms.CharField(widget=forms.TextInput(attrs={'id':'myField'}),label='', required=False)
        for visible in self.visible_fields():
            if visible.errors:
                visible.field.widget.attrs['class'] = 'form-control is-invalid'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

class UserAdminChangeForm(forms.ModelForm):
    passowrd1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    passowrd2 = forms.CharField(label='Password confirm', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if len(password1) > 7:
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError(
                        "Password and Confirm Password didn't match"
                    )
        else:
            raise forms.ValidationError(
                "Password must have atleast 8 characters"
            )

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["passowrd1"])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    pass

class PhoneVerificationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone_number',)

    def __init__(self, *args, **kwargs):
        super(PhoneVerificationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.errors:
                visible.field.widget.attrs['class'] = 'form-control is-invalid'
            else:
                visible.field.widget.attrs['class'] = 'form-control'


class OTPVerificationForm(forms.ModelForm):
    class Meta:
        model = PhoneOTP
        fields= ('otp',)

    def __init__(self, *args, **kwargs):
        super(OTPVerificationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.errors:
                visible.field.widget.attrs['class'] = 'form-control is-invalid'
            else:
                visible.field.widget.attrs['class'] = 'form-control'


class Register(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('name','email')

    def clean(self):
        cleaned_data = super(Register, self).clean()
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if len(password) > 7:
            if password and confirm_password and password != confirm_password:
                raise forms.ValidationError(
                        "Password and Confirm Password didn't match"
                    )
        else:
            raise forms.ValidationError(
                "Password must have atleast 8 characters"
            )

    def __init__(self, *args, **kwargs):
        super(Register, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.errors:
                visible.field.widget.attrs['class'] = 'form-control is-invalid'
            else:
                visible.field.widget.attrs['class'] = 'form-control'
