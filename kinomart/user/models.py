from django.db import models
from django.contrib.auth.models import AbstractUser

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


    