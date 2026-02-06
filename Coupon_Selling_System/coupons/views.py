# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.db import transaction

# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from .models import Coupon, Wallet, Purchase, Transaction
# import uuid


# # =========================
# # COUPON LIST (PUBLIC)
# # =========================





# def coupon_list(request):
#     coupons = Coupon.objects.filter(is_sold=False)

#     category = request.GET.get("category")
#     search = request.GET.get("search")

#     if category:
#         coupons = coupons.filter(category__iexact=category)

#     if search:
#         coupons = coupons.filter(code__icontains=search)

#     data = []
#     for c in coupons:
#         data.append({
#             "id": c.id,
#             "code": c.code,
#             "category": c.category,
#             "price": c.price,
#         })

#     return JsonResponse(data, safe=False)


# # =========================
# # MY COUPONS (SELLER DASHBOARD)
# # =========================
# @api_view(["GET"])
# def my_coupons(request):
#     user = request.user

#     # testing fallback
#     if not user.is_authenticated:
#         from django.contrib.auth.models import User
#         user = User.objects.first()

#     coupons = Coupon.objects.filter(seller=user)

#     data = []
#     for c in coupons:
#         data.append({
#             "id": c.id,
#             "code": c.code,
#             "category": c.category,
#             "price": c.price,
#             "is_sold": c.is_sold,
#         })

#     return Response(data)


# # =========================
# # SECURE BUY COUPON
# # =========================
# @api_view(["POST"])
# def buy_coupon(request, coupon_id):
#     user = request.user

#     if not user.is_authenticated:
#         from django.contrib.auth.models import User
#         user = User.objects.first()

#     try:
#         with transaction.atomic():
#             coupon = Coupon.objects.select_for_update().get(
#                 id=coupon_id, is_sold=False
#             )

#             wallet = Wallet.objects.select_for_update().get(user=user)

#             if wallet.balance < coupon.price:
#                 return Response({"error": "Insufficient balance"}, status=400)

#             wallet.balance -= coupon.price
#             wallet.save()

#             coupon.is_sold = True
#             coupon.save()

#             Purchase.objects.create(user=user, coupon=coupon)

#             Transaction.objects.create(
#                 user=user,
#                 amount=coupon.price,
#                 transaction_type="DEBIT",
#                 description=f"Purchased coupon {coupon.code}",
#             )

#         return Response({
#             "message": "Coupon purchased successfully",
#             "remaining_balance": wallet.balance
#         })

#     except Coupon.DoesNotExist:
#         return Response({"error": "Coupon not available"}, status=404)


# # =========================
# # RAZORPAY DUMMY – CREATE ORDER
# # =========================
# @method_decorator(csrf_exempt, name="dispatch")
# class CreateOrderAPIView(APIView):
#     def post(self, request):
#         amount = request.data.get("amount")

#         if not amount or int(amount) <= 0:
#             return Response({"error": "Invalid amount"}, status=400)

#         order_id = f"order_{uuid.uuid4().hex[:10]}"

#         return Response({
#             "order_id": order_id,
#             "amount": int(amount),
#             "currency": "INR"
#         })


# # =========================
# # PAYMENT SUCCESS – WALLET RECHARGE
# # =========================
# @csrf_exempt
# @api_view(["POST"])
# def payment_success(request):
#     amount = request.data.get("amount")

#     if not amount:
#         return Response({"error": "Amount required"}, status=400)

#     amount = int(amount)
#     if amount <= 0:
#         return Response({"error": "Invalid amount"}, status=400)

#     user = request.user
#     if not user.is_authenticated:
#         from django.contrib.auth.models import User
#         user = User.objects.first()

#     wallet, _ = Wallet.objects.get_or_create(user=user)
#     wallet.balance += amount
#     wallet.save()

#     Transaction.objects.create(
#         user=user,
#         amount=amount,
#         transaction_type="CREDIT",
#         description="Wallet recharge (Dummy Razorpay)",
#     )

#     return Response({
#         "message": "Payment successful",
#         "new_balance": wallet.balance
#     })


from decimal import Decimal
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
import uuid
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout




from .models import Coupon, Wallet, Purchase, Transaction


# =========================
# HOME
# =========================
def home(request):
    coupons = Coupon.objects.filter(is_sold=False).order_by("-created_at")[:6]
    return render(request, 'core/index.html', {"coupons": coupons})


# =========================
# BROWSE CATEGORY
# =========================
def browse_category(request, category_slug):
    category_map = {
        'electronics': 'Electronics',
        'fashion': 'Fashion',
        'food': 'Food & Dining',
        'travel': 'Travel',
        'shopping': 'Shopping',
        'gaming': 'Gaming'
    }

    coupons = Coupon.objects.filter(
        category__iexact=category_slug,
        is_sold=False
    )

    context = {
        'display_name': category_map.get(category_slug, 'All Categories'),
        'category_slug': category_slug,
        'coupons': coupons
    }
    return render(request, 'core/browse.html', context)


# =========================
# CATEGORY PAGES
# =========================
def electronics_view(request):
    return render(request, 'core/categories/electronics.html')

def food_view(request):
    return render(request, 'core/categories/food.html')

def gaming_view(request):
    return render(request, 'core/categories/gaming.html')


def travel_view(request):
    return render(request, 'core/categories/travel.html')


def shopping_view(request):
    return render(request, 'core/categories/shopping.html')


def dashboard(request):

    # Coupons the user is SELLING
    selling_coupons = Coupon.objects.filter(seller=request.user)

    my_coupons = [{
        "id": c.id,
        "code": c.code,
        "category": c.category,
        "price": c.selling_price,
        "is_sold": c.is_sold
    } for c in selling_coupons]

    # Coupons the user has BOUGHT
    purchases = Purchase.objects.filter(user=request.user).select_related("coupon")

    bought_coupons = [{
        "id": p.coupon.id,
        "code": p.coupon.code,
        "category": p.coupon.category,
        "price": p.coupon.selling_price,
        "is_sold": p.coupon.is_sold
    } for p in purchases]

    return render(request, 'core/dashboardo.html', {
        "mycoupons": my_coupons,          # selling
        "bought_coupons": bought_coupons # buying
    })



# =========================
# ALL COUPONS
# =========================
def all_coupons_view(request):
    coupons = Coupon.objects.filter(is_sold=False)
    return render(request, 'core/categories/all.html', {"coupons": coupons})

def coupon_detail_view(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)

    return render(request, "core/couponDetail.html", {
        "coupon": coupon
    })



# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid email or password")
        return redirect("login")

    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")




# =========================
# SIGNUP
# =========================
def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        terms = request.POST.get("terms")

        # Basic validation
        if not full_name or not email or not password or not confirm_password:
            messages.error(request, "All fields are required")
            return redirect("signup")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Account with this email already exists")
            return redirect("signup")

        # Create user (email used as username)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        # SAFE wallet creation (prevents IntegrityError)
        Wallet.objects.get_or_create(user=user)

        login(request, user)
        return redirect("dashboard")

    return render(request, "core/signup.html")



# =========================
# LIST COUPON (SELLER)
# =========================

def addcouponview(request):
    if request.method == "POST":
        try:
            Coupon.objects.create(
                seller=request.user,
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                brand=request.POST.get("brand"),
                category=request.POST.get("category"),
                selling_price=request.POST.get("price"),
                original_price=request.POST.get("original_price") or 0,
                discount_percent=request.POST.get("discount"),
                code=request.POST.get("coupon_code"),
                valid_until=request.POST.get("valid_until"),
                terms=request.POST.get("terms", ""),
            )
            return redirect("dashboard")

        except IntegrityError:
            return render(request, "core/addcoupon.html", {
                "error": "Coupon code already exists"
            })

    return render(request, "core/addcoupon.html")

    # return render(request, 'core/list_coupon.html')

#used to add Coupon view to create the coupon
def list_coupon_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        Coupon.objects.create(
            seller=request.user,
            code=request.POST.get("code"),
            category=request.POST.get("category"),
            price=request.POST.get("price"),
        )
        return redirect("my-coupons")
    return render(request, 'core/list_coupon.html')


def profile_page(request):
    user = request.user  # built-in Django User object
    
    context = {
        "user": user,
    }
    return render(request,"core/ProfilePage.html",{"user":context})


# =========================
# API: COUPON LIST
# =========================
def coupon_list(request):
    coupons = Coupon.objects.filter(is_sold=False)

    category = request.GET.get("category")
    search = request.GET.get("search")

    if category:
        coupons = coupons.filter(category__iexact=category)
    if search:
        coupons = coupons.filter(code__icontains=search)

    data = [{
        "id": c.id,
        "code": c.code,
        "category": c.category,
        "price": c.price
    } for c in coupons]

    return JsonResponse(data, safe=False)


# =========================
# API: MY COUPONS
# =========================
# @api_view(["GET"])
# def my_coupons(request):
#     if not request.user.is_authenticated:
#         return Response({"error": "Authentication required"}, status=401)

#     coupons = Coupon.objects.filter(seller=request.user)

#     data = [{
#         "id": c.id,
#         "code": c.code,
#         "category": c.category,
#         "price": c.price,
#         "is_sold": c.is_sold
#     } for c in coupons]

#     return Response(data)


# =========================
# API: BUY COUPON
# =========================


def checkout_page(request,coupon_id):
    coupon = get_object_or_404(Coupon,id=coupon_id)
    gst = coupon.selling_price * Decimal("0.18")
    total = coupon.selling_price + gst

    context = {
        "coupon":coupon,
        "gst":gst,
        "total":total
    }
    return render(request,'core/buying_page.html',context)


@login_required(login_url="signup")
def buy_coupon(request, coupon_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    try:
        with transaction.atomic():
            coupon = Coupon.objects.select_for_update().get(
                id=coupon_id,
                is_sold=False
            )

            coupon.is_sold = True
            coupon.save()

            Purchase.objects.create(
                user=request.user,
                coupon=coupon
            )

        return redirect("dashboard")

    except Coupon.DoesNotExist:
        return HttpResponseBadRequest("Coupon not available")



# =========================
# API: CREATE ORDER (DUMMY)
# =========================
@method_decorator(csrf_exempt, name="dispatch")
class CreateOrderAPIView(APIView):
    def post(self, request):
        amount = request.data.get("amount")

        if not amount or int(amount) <= 0:
            return Response({"error": "Invalid amount"}, status=400)

        return Response({
            "order_id": f"order_{uuid.uuid4().hex[:10]}",
            "amount": int(amount),
            "currency": "INR"
        })


# =========================
# API: PAYMENT SUCCESS
# =========================
@csrf_exempt
@api_view(["POST"])
def payment_success(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    amount = request.data.get("amount")
    if not amount or int(amount) <= 0:
        return Response({"error": "Invalid amount"}, status=400)

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet.balance += int(amount)
    wallet.save()

    Transaction.objects.create(
        user=request.user,
        amount=amount,
        transaction_type="CREDIT",
        description="Wallet recharge (Dummy Razorpay)",
    )

    return Response({
        "message": "Payment successful",
        "new_balance": wallet.balance
    })
