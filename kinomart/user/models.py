from django.db import models
from django.contrib.auth.models import AbstractUser
from products.models import ProductVarient

# Create your models here.
class User(AbstractUser):
    
    phone = models.CharField(max_length=50)
    

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
    payment_method = models.CharField(max_length=20)
    delivery_instructions = models.TextField(null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(ProductVarient, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)