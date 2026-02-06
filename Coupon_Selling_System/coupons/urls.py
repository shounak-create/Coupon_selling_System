from django.urls import path
from . import views

urlpatterns = [
    path("coupons/", views.coupon_list),
    # path("my-coupons/", views.my_coupons),
    path("buy/<int:coupon_id>/", views.buy_coupon),

    path("payment/create-order/", views.CreateOrderAPIView.as_view()),
    path("payment/success/", views.payment_success),

    path('', views.home, name='home'),
    path('browse/<str:category_name>/', views.browse_category, name='browse_category'),
    path('electronics/', views.electronics_view, name='electronics_page'),
    path('food/', views.food_view, name='food_page'),
    path('gaming/', views.gaming_view, name='gaming_page'),
    path('travel/', views.travel_view, name='travel_page'),
    path('shopping/', views.shopping_view, name='shopping_page'),
    path('all-coupons/', views.all_coupons_view, name='all_coupons_page'),
    path("coupon/<int:coupon_id>/", views.coupon_detail_view, name="coupon_detail"),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path("logout/", views.logout_view, name="logout"),
    path('list_coupon/', views.list_coupon_view, name='list_coupon'),
    path('add_coupon/', views.addcouponview, name='add_coupon'),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('profile/',views.profile_page,name="profile"),
    path("checkout/<int:coupon_id>/",views.checkout_page,name="checkout_page"),
    path('buy/<int:coupon_id>/', views.buy_coupon, name='buy_coupon'),

]
