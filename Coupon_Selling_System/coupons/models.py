from django.db import models
from django.contrib.auth.models import User


# =========================
# WALLET
# =========================
class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet"
    )
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Wallet ₹{self.balance}"


# =========================
# COUPON
# =========================
class Coupon(models.Model):
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coupons"
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    brand = models.CharField(max_length=100)

    CATEGORY_CHOICES = [
        ("Electronics", "Electronics"),
        ("Fashion", "Fashion"),
        ("Food", "Food"),
        ("Travel", "Travel"),
        ("Gaming", "Gaming"),
        ("Entertainment", "Entertainment"),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2,default=0
    )
    discount_percent = models.IntegerField(default=0)

    code = models.CharField(max_length=50, unique=True)
    valid_until = models.DateField()

    terms = models.TextField(blank=True, default="")

    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code



# =========================
# PURCHASE
# =========================
class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    coupon = models.OneToOneField(
        Coupon,
        on_delete=models.CASCADE,
        related_name="purchase"
    )
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bought {self.coupon.code}"


# =========================
# TRANSACTION
# =========================
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    amount = models.IntegerField()
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type} | ₹{self.amount}"
