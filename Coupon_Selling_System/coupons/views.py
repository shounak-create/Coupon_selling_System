from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Coupon
from datetime import datetime
from django.db.models import Q



@login_required
def add_coupon(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        brand = request.POST.get('brand')
        discount = request.POST.get('discount')
        category = request.POST.get('category')
        coupon_code = request.POST.get('coupon_code')
        price = request.POST.get('price')
        expiry_date = request.POST.get('expiry_date')

        if not all([title, brand, discount, category, coupon_code, price, expiry_date]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        Coupon.objects.create(
            seller=request.user,
            title=title,
            brand=brand,
            discount=discount,
            category=category,
            coupon_code=coupon_code,
            price=price,
            expiry_date=expiry_date
        )
        
from django.utils.timezone import now
def coupon_list(request):
    coupons = Coupon.objects.filter(
        is_sold=False,
        expiry_date__gte=now().date()
    )

    category = request.GET.get('category')
    brand = request.GET.get('brand')
    search = request.GET.get('search')

    if category:
        coupons = coupons.filter(category__iexact=category)

    if brand:
        coupons = coupons.filter(brand__icontains=brand)

    if search:
        coupons = coupons.filter(
            Q(title__icontains=search) |
            Q(brand__icontains=search) |
            Q(discount__icontains=search)
        )

    data = []
    for coupon in coupons:
        data.append({
            'id': coupon.id,
            'title': coupon.title,
            'brand': coupon.brand,
            'discount': coupon.discount,
            'category': coupon.category,
            'price': coupon.price,
            'expiry_date': coupon.expiry_date,
            'seller': coupon.seller.username
        })

    return JsonResponse({'coupons': data})



