#En este archivo esta el comando para el scraping 
from django.core.management.base import BaseCommand
from shopping.scraper import scrapear_todo

class Command(BaseCommand):
    help = 'Realiza scraping de productos desde varias tiendas y los guarda en la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando scraping...'))
        scrapear_todo()
        self.stdout.write(self.style.SUCCESS('Scraping completado y productos guardados.'))
