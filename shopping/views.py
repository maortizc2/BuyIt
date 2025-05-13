from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, SearchHistory
from django.db.models import Q
from .comparador import comparar_dos_productos_ai


def home(request):
    context = {}
    if request.user.is_authenticated:
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
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=query)

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'buscar.html', context)

@login_required
def historial_busquedas(request):
    historial = request.user.search_history.order_by('-timestamp')[:20]  # últimas 20
    return render(request, 'historial.html', {'historial': historial})

def productos_externos(request):
    productos = Product.objects.all().order_by('-created_at')
    return render(request, 'externos.html', {'productos': productos})


@login_required
def comparar_productos(request):
    if request.method == 'POST':
        id_1 = request.POST.get('producto_a')
        id_2 = request.POST.get('producto_b')

        if not (id_1 and id_2):
            return redirect('home')

        producto_a = Product.objects.filter(id=id_1).first()
        producto_b = Product.objects.filter(id=id_2).first()

        if not (producto_a and producto_b):
            return redirect('home')

        analisis_ai = comparar_dos_productos_ai(producto_a, producto_b)

        context = {
            'producto_a': {
                'nombre': producto_a.productName,
                'precio': f"${producto_a.productPrice:,.0f}",
                'categoria': producto_a.productCategory,
                'origen': producto_a.productOrigin,
                'imagen': producto_a.productPicture,
                'link': producto_a.productBuyLink
            },
            'producto_b': {
                'nombre': producto_b.productName,
                'precio': f"${producto_b.productPrice:,.0f}",
                'categoria': producto_b.productCategory,
                'origen': producto_b.productOrigin,
                'imagen': producto_b.productPicture,
                'link': producto_b.productBuyLink
            },
            'analisis_ai': analisis_ai
        }

        return render(request, 'comparacion.html', context)

    return redirect('home')