from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle-favorito/<int:producto_id>/', views.toggle_favorito, name='toggle_favorito'),
    path('favoritos/', views.favoritos_view, name='favoritos_view'),
    path('search/', views.search_products, name='search_products'),
    path('products/', views.productos_externos, name='productos_externos'),
    path('comparar/', views.comparar_productos, name='comparar_productos'),  
    path('historial/', views.historial_busquedas, name='historial_busquedas'),
]
