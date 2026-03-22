from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'price', 'in_stock', 'category', 'created_at')
    list_filter = ('in_stock', 'is_active', 'category')
    search_fields = ('name', 'shop__name')
    list_editable = ('in_stock',)
