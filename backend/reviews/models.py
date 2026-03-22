from django.db import models
from django.conf import settings
from shops.models import Shop

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6)])
    comment = models.TextField()
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'shop')

    def __str__(self):
        return f"{self.user.username} -> {self.shop.name} ({self.rating}★)"
