from django.contrib import admin
from .models import Product, SearchHistory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('productName', 'productBrand', 'productPrice', 'productCategory', 'productStock', 'created_at')
    search_fields = ('productName', 'productBrand', 'productCategory')
    list_filter = ('productCategory', 'productBrand', 'productOrigin')
    ordering = ('-created_at',)