from django.urls import path
from . import views  # Importa las vistas de la carpeta 'shopping'

urlpatterns = [
    # Ruta para la página inicial que llama a la vista 'home'
    path('', views.home, name='home'),
    path('toggle-favorito/<int:producto_id>/', views.toggle_favorito, name='toggle_favorito'),
    path('favoritos/', views.favoritos_view, name='favoritos_view'),
    path('search/', views.search_products, name='search_products'),
]
