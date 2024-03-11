from django.db import models
from offer.models import Offer

# Create your models here.

class Category(models.Model):
    category=models.CharField(max_length=50)
    offer=models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.category


class SubCategory(models.Model):
    sub_category=models.CharField(max_length=50)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='subcategories')
   
    def __str__(self) -> str:
        return self.sub_category

    

class Unit(models.Model):
    name=models.CharField(max_length=10,null=True)
    unit=models.CharField(max_length=5)
    def __str__(self) -> str:
        return f'{self.unit}'

class Brand(models.Model):
    brand_name=models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.brand_name


class Products(models.Model):
    product_name=models.CharField(max_length=100)
    description=models.TextField(max_length=300)
    sub_category = models.ForeignKey(SubCategory,on_delete=models.SET_NULL,null=True, related_name='products')
    brand=models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True)
    is_offer=models.BooleanField(default=False)
    offer=models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self) -> str:
        return self.product_name

class ProductImages(models.Model):
    image=models.ImageField()
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE,null=True,related_name='images')



class ProductVarient(models.Model):
    quantity=models.FloatField()
    unit=models.ForeignKey(Unit,on_delete=models.SET_NULL,null=True)
    stock=models.FloatField()
    price=models.DecimalField(max_digits=8,decimal_places=2)
    offer_price=models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE, related_name='varients')
    is_holded=models.BooleanField(default=False)

    

    def __str__(self) -> str:
        return f'{self.product_id}'