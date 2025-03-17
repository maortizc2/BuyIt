from django.shortcuts import render
from .models import Product

def home(request):
    context = {}
    if request.user.is_authenticated:
        # Solo se consultan y envían los productos si el usuario está autenticado.
        context['productos'] = Product.objects.all()
    return render(request, 'home.html', context)
