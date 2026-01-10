from django.urls import path
from . import views

urlpatterns = [
    path('add-coupon/', views.add_coupon, name='add_coupon'),
    path('coupons/', views.coupon_list, name='coupon_list'),

]
