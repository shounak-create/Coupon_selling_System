from django.contrib import admin
from .models import Coupon, Wallet, Purchase, Transaction

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "category", "price", "seller", "is_sold")
    list_filter = ("category", "is_sold")
    search_fields = ("code", "category")

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "coupon", "purchased_at")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "transaction_type", "description", "created_at")
