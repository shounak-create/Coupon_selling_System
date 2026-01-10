from django.db import models
from django.contrib.auth.models import User

class Coupon(models.Model):
    CATEGORY_CHOICES = (
        ('Food', 'Food'),
        ('Shopping', 'Shopping'),
        ('Grocery', 'Grocery'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.IntegerField()
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=1000)

    def __str__(self):
        return f"{self.user.username} Wallet"
