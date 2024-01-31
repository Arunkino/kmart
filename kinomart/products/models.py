from django.db import models

# Create your models here.

class Category(models.Model):
    category=models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.category


class SubCategory(models.Model):
    sub_category=models.CharField(max_length=50)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='subcategories')
   
    def __str__(self) -> str:
        return self.sub_category

    

class Unit(models.Model):
    unit=models.CharField(max_length=10)
    def __str__(self) -> str:
        return f'{self.unit}'

class Brand(models.Model):
    brand_name=models.CharField(max_length=50)


class Products(models.Model):
    product_name=models.CharField(max_length=100)
    description=models.TextField(max_length=300)
    sub_category = models.ForeignKey(SubCategory,on_delete=models.SET_NULL,null=True, related_name='products')
    brand=models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True)
    is_offer=models.BooleanField(default=False)
    

class ProductImages(models.Model):
    image=models.ImageField()
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE,null=True,related_name='images')



class ProductVarient(models.Model):
    quantity=models.FloatField()
    unit=models.ForeignKey(Unit,on_delete=models.SET_NULL,null=True)
    stock=models.FloatField()
    price=models.FloatField()
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE, related_name='varients')
    is_holded=models.BooleanField(default=False)
