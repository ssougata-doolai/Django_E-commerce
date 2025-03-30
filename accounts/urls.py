from django.urls import path
from .import views
from accounts.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
#from .views import AddressFormView
app_name = 'accounts'

urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',auth_views.LoginView.as_view(template_name='accounts/login.html',authentication_form=AuthenticationForm),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='accounts/logout.html'),name='logout'),
#    path('add_address/',AddressFormView.as_view(), name='add-address'),
    path('add_address/',views.add_address, name='add-address'),
    path('update-address/<pk>/',views.update_address, name='update-address'),
    path('activate/<activation_key>/', views.activation_view, name="activation-view"),
    path('verify-phone/',views.validate_phone, name='verify-phone'),
    path('verify-otp/',views.validate_otp, name='verify-otp'),
]
