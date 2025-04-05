#este archivo es para ejecutar el scrapping cuando se inicia seccion

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from .scraper import scrapear_todo  # Importa tu función de scraping

@receiver(user_logged_in)
def execute_scraping_on_login(sender, user, request, **kwargs):
    """Ejecutar scraping cuando un usuario inicia sesión"""
    # Opcional: Verificar si es un usuario específico o con permisos específicos
    if user.is_staff or user.has_perm('shopping.can_scrape'):
        # Ejecutar en segundo plano para no bloquear la respuesta HTTP
        from threading import Thread
        scraping_thread = Thread(target=scrapear_todo)
        scraping_thread.daemon = True
        scraping_thread.start()