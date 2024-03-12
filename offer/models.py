from django.db import models
from datetime import datetime,timedelta

# Create your models here.


class Offer(models.Model):
    offer_name=models.CharField(max_length=100)
    discount=models.DecimalField(max_digits=5,decimal_places=2)
    expiry_date=models.DateField(default=datetime.now()+timedelta(days=30))


    

    def __str__(self) -> str:
        return self.offer_name
