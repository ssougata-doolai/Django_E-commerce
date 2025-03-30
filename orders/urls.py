from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'orders'

urlpatterns = [
    path('all-orders/',views.view_order, name='view-order-all'),
    path('shipped-orders/',views.shipped_order, name='view-shipped-order'),
    path('place-order/',views.place_order, name='place-order'),
    path('set-address/<pk>/',views.set_address, name='set-address'),
    path('payment/<order_id>/', views.payment, name='payment'),
    path('details/<order_id>/', views.order_details, name='details'),
    path('order-summary/<order_id>/', views.order_summary, name='order-summary'),
    path('invoice/<order_id>/', views.order_invoice, name='invoice'),
    path('cancel-order/<order_id>/',views.cancel_order, name='cancel-order'),
    path('track-order/<order_id>/', views.track_order, name='track'),
    path('payment/handleRequest/<order_id>/<txnToken>/', views.handle_payment_request, name='handle-request'),
]
