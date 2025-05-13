from django.contrib import admin
from .models import Product, SearchHistory

# Register your models here.
admin.site.register(Product)
admin.site.register(SearchHistory)