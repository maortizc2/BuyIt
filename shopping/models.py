from django.db import models
from django.contrib.auth.models import User

#clase producto , almacena todos los atributos de producto
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
    productLink = models.URLField(unique=False)  # Para evitar productos repetidos
    productOrigin = models.CharField(max_length=100, default='')  # Página web origen
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Relación ManyToMany para productos favoritos
    favorited_by = models.ManyToManyField(User, related_name='favorite_products', blank=True)

    def __str__(self):
        return self.productName

# clase de busqueda , almacena todos los datos necesarios para filtrar los articulos  
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query}"

# clase de reviews , almacena todos los datos necesarios para almacenar los comentarios
class Review(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reseñas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    calificacion = models.IntegerField()  # de 1 a 5
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.productName} ({self.calificacion}/5)"

