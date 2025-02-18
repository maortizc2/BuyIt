from django.db import models

class Product(models.Model):
    productName = models.CharField(max_length=200)
    productDescription = models.TextField()
    productPicture = models.URLField()  # Usamos URLField para imágenes externas
    productPrice = models.DecimalField(max_digits=10, decimal_places=2)
    productCategory = models.CharField(max_length=100, choices=[
        ('Camisetas', 'Camisetas'),
        ('Pantalones', 'Pantalones'),
        ('Zapatos', 'Zapatos'),
        ('Chaquetas', 'Chaquetas'),
        ('Accesorios', 'Accesorios'),
        ('Otros', 'Otros')
    ])
    productBrand = models.CharField(max_length=100)  # Para almacenar la marca
    productStock = models.PositiveIntegerField(default=10)  # Un control de stock simple
    productBuyLink = models.URLField()  # Link oficial de compra
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.productName
