from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shops.models import Shop, Category
from products.models import Product

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@localbazar.com', 'admin123')
            admin.role = 'admin'
            admin.save()
            self.stdout.write('Created admin user: admin / admin123')

        # Employee
        emp, _ = User.objects.get_or_create(username='employee1', defaults={
            'email': 'employee@localbazar.com', 'role': 'employee'
        })
        emp.set_password('emp123')
        emp.save()

        # Seller
        seller, _ = User.objects.get_or_create(username='seller1', defaults={
            'email': 'seller@localbazar.com', 'role': 'seller', 'phone': '03001234567'
        })
        seller.set_password('seller123')
        seller.save()

        # Categories
        cats_data = [
            ('Grocery', '🛒', 'grocery'), ('Electronics', '📱', 'electronics'),
            ('Clothing', '👕', 'clothing'), ('Food', '🍕', 'food'),
            ('Pharmacy', '💊', 'pharmacy'), ('Books', '📚', 'books'),
        ]
        cats = {}
        for name, icon, slug in cats_data:
            c, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon})
            cats[slug] = c

        # Shops
        shops_data = [
            ('Al-Fatah Store', 'Super grocery store', 'F-6 Markaz, Islamabad', 'Islamabad', 33.7294, 73.0931, '03001111111', 'grocery'),
            ('Tech World', 'Latest electronics', 'G-9 Markaz, Islamabad', 'Islamabad', 33.6938, 73.0651, '03002222222', 'electronics'),
            ('City Pharmacy', 'Medicines & health', 'Blue Area, Islamabad', 'Islamabad', 33.7215, 73.0898, '03003333333', 'pharmacy'),
            ('Fashion Hub', 'Trendy clothing', 'Centaurus Mall, Islamabad', 'Islamabad', 33.7120, 73.0591, '03004444444', 'clothing'),
        ]
        for s_data in shops_data:
            shop, created = Shop.objects.get_or_create(name=s_data[0], defaults={
                'description': s_data[1], 'address': s_data[2], 'city': s_data[3],
                'latitude': s_data[4], 'longitude': s_data[5], 'phone': s_data[6],
                'category': cats[s_data[7]], 'owner': seller, 'is_verified': True
            })
            if created:
                # Add some products
                Product.objects.create(shop=shop, name='Sample Product 1', price=500, category=cats[s_data[7]], in_stock=True)
                Product.objects.create(shop=shop, name='Sample Product 2', price=1200, category=cats[s_data[7]], in_stock=True)

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
        self.stdout.write('Login: admin/admin123 | seller1/seller123 | employee1/emp123')
