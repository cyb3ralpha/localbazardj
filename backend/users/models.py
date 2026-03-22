from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Employee-specific: which shops they manage
    managed_shops = models.ManyToManyField('shops.Shop', blank=True, related_name='employees')

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin_or_employee(self):
        return self.role in ('admin', 'employee') or self.is_staff
