from django.contrib import admin
from .models import Product, SearchHistory

<<<<<<< HEAD
# Register your models here.
admin.site.register(Product)
admin.site.register(SearchHistory)
=======
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('productName', 'productBrand', 'productPrice', 'productCategory', 'productStock', 'created_at')
    search_fields = ('productName', 'productBrand', 'productCategory')
    list_filter = ('productCategory', 'productBrand', 'productOrigin')
    ordering = ('-created_at',)
>>>>>>> cc08e4e (💡 Comparador de productos funcional + UI animada)
