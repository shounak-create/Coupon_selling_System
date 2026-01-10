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
    coupons = Coupon.objects.filter(is_sold=False)

    category = request.GET.get('category')
    search = request.GET.get('search')

    if category:
        coupons = coupons.filter(category__icontains=category)

    if search:
        coupons = coupons.filter(code__icontains=search)

    data = []
    for c in coupons:
        data.append({
            "id": c.id,
            "code": c.code,
            "category": c.category,
            "price": c.price,
            "seller": c.seller.username
        })

    return JsonResponse(data, safe=False)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Coupon, Wallet, Transaction

@login_required
def buy_coupon(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id, is_sold=False)
    except Coupon.DoesNotExist:
        return JsonResponse({"error": "Coupon not available"}, status=400)

    buyer = request.user
    seller = coupon.seller

    buyer_wallet = Wallet.objects.get(user=buyer)
    seller_wallet = Wallet.objects.get(user=seller)

    if buyer_wallet.balance < coupon.price:
        return JsonResponse({"error": "Insufficient balance"}, status=400)

    # 💰 WALLET TRANSFER
    buyer_wallet.balance -= coupon.price
    seller_wallet.balance += coupon.price

    buyer_wallet.save()
    seller_wallet.save()

    # 🔒 LOCK COUPON
    coupon.is_sold = True
    coupon.save()

    # 🧾 TRANSACTION
    Transaction.objects.create(
        buyer=buyer,
        seller=seller,
        coupon=coupon,
        amount=coupon.price
    )

    return JsonResponse({
        "message": "Payment successful",
        "coupon_code": coupon.code
    })

