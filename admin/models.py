from django.db import models
from datetime import datetime, timedelta
from user.models import User

# Create your models here.

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=50,unique=True)
    count=models.IntegerField(default=50)
    expiry_date=models.DateField(default=datetime.now()+timedelta(days=30))
    min_order=models.DecimalField(max_digits=6, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

class AppliedCoupon(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)