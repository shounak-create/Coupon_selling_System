from django.contrib import admin
from .models import Wallet, Coupon, Purchase, Transaction


# =========================
# WALLET ADMIN
# =========================
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "balance",
        "created_at",
    )
    search_fields = ("user__username",)
    readonly_fields = ("created_at",)


# =========================
# COUPON ADMIN
# =========================
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "brand",
        "category",
        "selling_price",
        "discount_percent",
        "is_sold",
        "valid_until",
        "created_at",
    )

    list_filter = (
        "brand",
        "category",
        "is_sold",
    )

    search_fields = (
        "code",
        "title",
        "brand",
    )

    readonly_fields = (
        "created_at",
    )


# =========================
# PURCHASE ADMIN
# =========================
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "coupon",
        "purchased_at",
    )

    search_fields = (
        "user__username",
        "coupon__code",
    )

    readonly_fields = (
        "purchased_at",
    )


# =========================
# TRANSACTION ADMIN
# =========================
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "transaction_type",
        "amount",
        "description",
        "created_at",
    )

    list_filter = (
        "transaction_type",
    )

    search_fields = (
        "user__username",
        "description",
    )

    readonly_fields = (
        "created_at",
    )
