from django.urls import path
from . import views
from .views import coupon_list, buy_coupon

urlpatterns = [
    path('add-coupon/', views.add_coupon, name='add_coupon'),
    path('coupons/', views.coupon_list, name='coupon_list'),
    path("coupons/", coupon_list),
    path("buy/<int:coupon_id>/", buy_coupon),

]
