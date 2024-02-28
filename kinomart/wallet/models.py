from django.db import models
from user.models import User
from datetime import datetime

# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=7, decimal_places=2,default=0)
    last_transaction=models.CharField(max_length=100,default="0.00")

class WalletTransactions(models.Model):
    wallet=models.ForeignKey(Wallet,on_delete=models.CASCADE)
    transaction_date=models.DateField(default=datetime.now())
    transaction_amount=models.DecimalField(max_digits=7, decimal_places=2)
    discription=models.CharField(max_length=150)


    
