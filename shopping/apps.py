from django.apps import AppConfig


class ShoppingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopping'

    def ready(self):
        import shopping.signals  # Importa las señales al iniciar la aplicación
