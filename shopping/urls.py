from django.urls import path
from . import views  # Importa las vistas de la carpeta 'shopping'

urlpatterns = [
    # Ruta para la página inicial que llama a la vista 'home'
    path('', views.home, name='home'),
]
