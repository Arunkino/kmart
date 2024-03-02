from django.db import models
from django.contrib.auth.models import AbstractUser
from products.models import ProductVarient,Products
import uuid
import base64

# Create your models here.
class User(AbstractUser):
    
    phone = models.CharField(max_length=50)
    referral_code=models.CharField(max_length=20,blank=True,null=True)
    
    def __str__(self) -> str:
        return self.first_name
    
    def generate_verification_code(self):
        return base64.urlsafe_b64encode(uuid.uuid1().bytes)[:15].decode("utf-8")

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_verification_code()
        return super(User, self).save(*args, **kwargs)



class UserAddress(models.Model):
    city= models.CharField(max_length=50,null=True)
    state= models.CharField(max_length=50,default='Kerala')
    landmark= models.CharField(max_length=50,null=True)
    pin= models.BigIntegerField()
    address_line=models.TextField()
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    is_default=models.BooleanField(default=True,null=True)


class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(ProductVarient,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    price=models.DecimalField(max_digits=6,decimal_places=2)

class   Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_instructions = models.TextField(null=True)
    status = models.CharField(max_length=20, default='Pending')
    return_status=models.CharField(max_length=50, null=True,blank=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    payment_method = models.CharField(max_length=20)
    payment_status = models.BooleanField(default=False)
    order_id=models.CharField(max_length=100,blank=True)
    razorpay_payment_id=models.CharField(max_length=100,blank=True)

    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(ProductVarient, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

class OrderAddress(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE, related_name='address')
    city= models.CharField(max_length=50,null=True)
    state= models.CharField(max_length=50,default='Kerala')
    landmark= models.CharField(max_length=50,null=True)
    pin= models.BigIntegerField()
    address_line=models.TextField(null=True)
    

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Products,on_delete=models.CASCADE)


class TempData(models.Model):
    payment_method=models.CharField(max_length=50)
    address_id=models.CharField(max_length=50)
    instructions=models.CharField(max_length=100,blank=True,null=True)
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    user=models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True,related_name='order_data')
    coupon_code=models.CharField(max_length=100,blank=True,null=True)
    order_id=models.CharField(max_length=100,blank=True)

