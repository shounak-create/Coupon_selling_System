from django.urls import path
from .views import coupon_list, buy_coupon
from .views import create_payment_order, payment_success

urlpatterns = [
    path("coupons/", coupon_list),
    path("buy/<int:coupon_id>/", buy_coupon),
    path("payment/create/", create_payment_order),
    path("payment/success/", payment_success),
    
    
]
