from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=1000)

    def __str__(self):
        return f"{self.user.username} Wallet"


class Coupon(models.Model):
    code = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    price = models.IntegerField()
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

