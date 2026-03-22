from django.db import models
from django.conf import settings
import math

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='🛒')
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name
    class Meta: verbose_name_plural = 'Categories'

class Shop(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shops')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='shop_covers/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.name
    def distance_from(self, lat, lng):
        R = 6371
        lat1,lon1 = math.radians(float(self.latitude)),math.radians(float(self.longitude))
        lat2,lon2 = math.radians(float(lat)),math.radians(float(lng))
        dlat,dlon = lat2-lat1, lon2-lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        return R*2*math.asin(math.sqrt(a))
    @property
    def avg_rating(self):
        revs = self.reviews.all()
        return round(sum(r.rating for r in revs)/revs.count(),1) if revs.exists() else 0.0
    @property
    def review_count(self): return self.reviews.count()
