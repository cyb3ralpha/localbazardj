from django.contrib import admin
from .models import Shop, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active', 'city', 'category')
    search_fields = ('name', 'owner__username', 'address')
    actions = ['verify_shops', 'deactivate_shops']

    def verify_shops(self, request, queryset):
        queryset.update(is_verified=True)
    verify_shops.short_description = "Verify selected shops"

    def deactivate_shops(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_shops.short_description = "Deactivate selected shops"
