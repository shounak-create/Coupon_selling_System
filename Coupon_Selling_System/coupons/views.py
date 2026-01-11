from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coupon, Wallet, Purchase, Transaction
import uuid


# ==================================================
# COUPON LIST (PUBLIC API)
# ==================================================
def coupon_list(request):
    coupons = Coupon.objects.filter(is_sold=False)

    category = request.GET.get("category")
    search = request.GET.get("search")

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


# ==================================================
# BASIC COUPON PURCHASE (OLD – KEEP FOR DEMO)
# ==================================================
@api_view(["POST"])
def buy_coupon(request, coupon_id):
    user = request.user

    # 🔧 testing fallback
    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()

    with transaction.atomic():
        coupon = get_object_or_404(Coupon, id=coupon_id, is_sold=False)
        wallet = Wallet.objects.select_for_update().get(user=user)

        if wallet.balance < coupon.price:
            return Response({"error": "Insufficient balance"}, status=400)

        wallet.balance -= coupon.price
        wallet.save()

        coupon.is_sold = True
        coupon.save()

        Purchase.objects.create(user=user, coupon=coupon)

    return Response({"message": "Coupon purchased successfully"})


# ==================================================
# 🔒 SECURE COUPON PURCHASE (INDUSTRY LEVEL)
# ==================================================
@api_view(["POST"])
def secure_buy_coupon(request, coupon_id):
    user = request.user

    # 🔧 testing fallback
    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()

    try:
        with transaction.atomic():

            coupon = Coupon.objects.select_for_update().get(
                id=coupon_id,
                is_sold=False
            )

            wallet = Wallet.objects.select_for_update().get(user=user)

            if wallet.balance < coupon.price:
                return Response({"error": "Insufficient balance"}, status=400)

            # 💸 DEBIT
            wallet.balance -= coupon.price
            wallet.save()

            # 🏷 MARK SOLD
            coupon.is_sold = True
            coupon.save()

            # 🧾 PURCHASE
            Purchase.objects.create(user=user, coupon=coupon)

            # 📘 TRANSACTION LOG
            Transaction.objects.create(
                user=user,
                amount=coupon.price,
                transaction_type="DEBIT",
                description=f"Purchased coupon {coupon.code}"
            )

        return Response({
            "message": "Coupon purchased securely",
            "coupon_code": coupon.code,
            "remaining_balance": wallet.balance
        })

    except Coupon.DoesNotExist:
        return Response({"error": "Coupon not available"}, status=404)


# ==================================================
# RAZORPAY DUMMY – CREATE ORDER
# ==================================================
@method_decorator(csrf_exempt, name="dispatch")
class CreateOrderAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # 🔴 later enable

    def post(self, request):
        amount = request.data.get("amount")

        if not amount or int(amount) <= 0:
            return Response({"error": "Invalid amount"}, status=400)

        order_id = f"order_{uuid.uuid4().hex[:10]}"

        return Response({
            "order_id": order_id,
            "amount": int(amount),
            "currency": "INR"
        })


# ==================================================
# PAYMENT SUCCESS – WALLET RECHARGE
# ==================================================
@csrf_exempt
@api_view(["POST"])
def payment_success(request):
    amount = request.data.get("amount")

    if not amount:
        return Response({"error": "Amount is required"}, status=400)

    amount = int(amount)
    if amount <= 0:
        return Response({"error": "Invalid amount"}, status=400)

    # 🔧 testing fallback
    user = request.user
    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()

    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance += amount
    wallet.save()

    Transaction.objects.create(
        user=user,
        amount=amount,
        transaction_type="CREDIT",
        description="Wallet recharge via Razorpay (Dummy)"
    )

    return Response({
        "message": "Payment successful",
        "new_balance": wallet.balance
    })
    
    # =========================
# SELLER – MY COUPONS API
# =========================
@api_view(["GET"])
def my_coupons(request):
    user = request.user

    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()  # testing fallback

    coupons = Coupon.objects.filter(seller=user)

    data = []
    for c in coupons:
        data.append({
            "id": c.id,
            "code": c.code,
            "category": c.category,
            "price": c.price,
            "is_sold": c.is_sold
        })

    return Response(data)

 #My Purchases API (BUYER)
@api_view(["GET"])
def my_purchases(request):
    user = request.user

    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()

    purchases = Purchase.objects.filter(user=user).select_related("coupon")

    data = []
    for p in purchases:
        data.append({
            "coupon_code": p.coupon.code,
            "price": p.coupon.price,
            "purchased_at": p.purchased_at
        })

    return Response(data)

#Wallet Balance API
@api_view(["GET"])
def wallet_balance(request):
    user = request.user

    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()

    wallet, _ = Wallet.objects.get_or_create(user=user)

    return Response({
        "balance": wallet.balance
    })


#Transaction History API
@api_view(["GET"])
def transaction_history(request):
    user = request.user

    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()

    transactions = Transaction.objects.filter(user=user).order_by("-id")

    data = []
    for t in transactions:
        data.append({
            "amount": t.amount,
            "type": t.transaction_type,
            "description": t.description
        })

    return Response(data)


#Earnings API (SELLER)
@api_view(["GET"])
def seller_earnings(request):
    user = request.user

    if not user.is_authenticated:
        from django.contrib.auth.models import User
        user = User.objects.first()

    earnings = Transaction.objects.filter(
        user=user,
        transaction_type="CREDIT"
    )

    total = sum(e.amount for e in earnings)

    return Response({
        "total_earnings": total
    })





