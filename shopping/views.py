from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from django.db.models import Q

def home(request):
    context = {}
    if request.user.is_authenticated:
        # Se consultan y envían los productos si el usuario está autenticado.
        context['productos'] = Product.objects.all()
    return render(request, 'home.html', context)

@login_required
def toggle_favorito(request, producto_id):
    producto = get_object_or_404(Product, id=producto_id)
    user = request.user
    if producto in user.favorite_products.all():
        user.favorite_products.remove(producto)
    else:
        user.favorite_products.add(producto)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def favoritos_view(request):
    favoritos = request.user.favorite_products.all()
    return render(request, 'favoritos.html', {'favoritos': favoritos})



def search_products(request):
    query = request.GET.get('q')
    results = Product.objects.none()
    if query:
        results = Product.objects.filter(
            Q(productName__icontains=query) | Q(productDescription__icontains=query)
        )
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'buscar.html', context)