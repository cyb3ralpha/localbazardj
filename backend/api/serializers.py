from rest_framework import serializers
from users.models import User
from shops.models import Shop, Category
from products.models import Product
from reviews.models import Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'avatar', 'is_verified', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_verified')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'phone')
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ShopSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = '__all__'
        read_only_fields = ('owner', 'is_verified', 'created_at', 'updated_at')

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

class ShopDetailSerializer(ShopSerializer):
    employees = serializers.SerializerMethodField()
    def get_employees(self, obj):
        return [{'id': e.id, 'username': e.username, 'email': e.email} for e in obj.employees.all()]

class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    shop_address = serializers.CharField(source='shop.address', read_only=True)
    shop_lat = serializers.DecimalField(source='shop.latitude', read_only=True, max_digits=10, decimal_places=7)
    shop_lng = serializers.DecimalField(source='shop.longitude', read_only=True, max_digits=10, decimal_places=7)
    shop_phone = serializers.CharField(source='shop.phone', read_only=True)
    shop_is_verified = serializers.BooleanField(source='shop.is_verified', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class AdminUserSerializer(serializers.ModelSerializer):
    shop_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'is_verified', 'is_active', 'created_at', 'shop_count')
    def get_shop_count(self, obj):
        return obj.shops.count() if obj.role == 'seller' else 0
