from django.db import models

# Create your models here.

class Product(models.Model):
    productName = models.CharField(max_length=100)
    productDescription = models.CharField(max_length=500)
    productPicture = models.ImageField(upload_to='productImages/')