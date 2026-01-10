import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Wallet, Payment

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Coupon, Wallet, Purchase

@api_view(["POST"])
def create_payment_order(request):
    user = request.user
    amount = request.data.get("amount")

    if not amount:
        return Response({"error": "Amount required"}, status=400)

    razorpay_order_id = "order_" + uuid.uuid4().hex

    return Response({
        "order_id": razorpay_order_id,
        "amount": amount,
        "currency": "INR"
    })

@api_view(["POST"])
def payment_success(request):
    user = request.user
    amount = int(request.data.get("amount"))
    order_id = request.data.get("order_id")

    wallet, _ = Wallet.objects.get_or_create(user=user)

    wallet.balance += amount
    wallet.save()

    Payment.objects.create(
        user=user,
        amount=amount,
        razorpay_order_id=order_id,
        razorpay_payment_id="pay_" + uuid.uuid4().hex,
        status="SUCCESS"
    )

    return Response({
        "message": "Wallet recharged successfully",
        "new_balance": wallet.balance
    })




# ✅ COUPON LIST + SEARCH + CATEGORY FILTER
@api_view(['GET'])
def coupon_list(request):
    coupons = Coupon.objects.filter(is_sold=False)

    category = request.GET.get('category')
    search = request.GET.get('search')

    if category:
        coupons = coupons.filter(category__iexact=category)

    if search:
        coupons = coupons.filter(code__icontains=search)

    data = []
    for c in coupons:
        data.append({
            "id": c.id,
            "code": c.code,
            "category": c.category,
            "price": c.price
        })

    return Response(data)


# ✅ BUY COUPON API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_coupon(request, coupon_id):
    user = request.user

    try:
        coupon = Coupon.objects.get(id=coupon_id, is_sold=False)
    except Coupon.DoesNotExist:
        return Response({"error": "Coupon not available"}, status=404)

    wallet, _ = Wallet.objects.get_or_create(user=user)

    if wallet.balance < coupon.price:
        return Response({"error": "Insufficient balance"}, status=400)

    wallet.balance -= coupon.price
    wallet.save()

    coupon.is_sold = True
    coupon.save()

    Purchase.objects.create(user=user, coupon=coupon)

    return Response({
        "message": "Coupon purchased successfully",
        "remaining_balance": wallet.balance
    })
