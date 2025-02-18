from django.shortcuts import render
from .models import Product

def home(request):
    productos = Product.objects.all()  # Obtener todos los productos
    return render(request, 'home.html', {'productos': productos})  # Enviar productos a la plantilla
