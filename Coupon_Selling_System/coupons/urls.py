from django.urls import path
from .views import (
    coupon_list,
    buy_coupon,
    CreateOrderAPIView,
    payment_success
)
from . import views


urlpatterns = [
    # Coupons
    path("coupons/", coupon_list, name="coupon_list"),
    path("buy/<int:coupon_id>/", buy_coupon, name="buy_coupon"),

    # Payment (Dummy Razorpay)
    path(
        "payment/create-order/",
        CreateOrderAPIView.as_view(),
        name="create_payment_order"
    ),
    path(
        "payment/success/",
        payment_success,
        name="payment_success"
    ),
    path("my-coupons/", views.my_coupons),
    path("my-purchases/", views.my_purchases),
    path("wallet/", views.wallet_balance),
    path("transactions/", views.transaction_history),
    path("earnings/", views.seller_earnings),
    
]
