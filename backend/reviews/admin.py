from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop', 'rating', 'is_flagged', 'created_at')
    list_filter = ('rating', 'is_flagged')
    actions = ['flag_reviews', 'unflag_reviews']
    def flag_reviews(self, request, queryset):
        queryset.update(is_flagged=True)
    def unflag_reviews(self, request, queryset):
        queryset.update(is_flagged=False)
