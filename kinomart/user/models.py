from django.db import models

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50,null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    is_active=models.BooleanField(default=True)

class UserAddress(models.Model):
    city= models.CharField(max_length=50,null=True)
    state= models.CharField(max_length=50,default='Kerala')
    landmark= models.CharField(max_length=50,null=True)
    pin= models.BigIntegerField()
    address_line=models.TextField()
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)


    