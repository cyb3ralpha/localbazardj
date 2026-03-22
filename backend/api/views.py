from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from users.models import User
from shops.models import Shop, Category
from products.models import Product
from reviews.models import Review
from .serializers import *
from .permissions import IsAdmin, IsAdminOrEmployee, IsSellerOrAdmin, IsShopOwnerOrAdmin

# ─── Auth ───────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

# ─── Search ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    q = request.GET.get('q', '').strip()
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = float(request.GET.get('radius', 10))
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category = request.GET.get('category')
    in_stock = request.GET.get('in_stock')

    products = Product.objects.filter(is_active=True, shop__is_active=True)
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(shop__name__icontains=q))
    if category:
        products = products.filter(category__slug=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if in_stock == 'true':
        products = products.filter(in_stock=True)

    results = []
    for p in products.select_related('shop', 'category'):
        d = None
        if lat and lng:
            d = p.shop.distance_from(lat, lng)
            if d > radius:
                continue
        data = ProductSerializer(p).data
        if d is not None:
            data['distance'] = round(d, 2)
        results.append(data)

    if lat and lng:
        results.sort(key=lambda x: x.get('distance') or 999)

    return Response({'count': len(results), 'results': results})

# ─── Shops ──────────────────────────────────────────────────────────────────

class NearbyShopsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = float(request.GET.get('radius', 10))
        category = request.GET.get('category')

        shops = Shop.objects.filter(is_active=True)
        if category:
            shops = shops.filter(category__slug=category)

        results = []
        for shop in shops:
            data = ShopSerializer(shop).data
            if lat and lng:
                d = shop.distance_from(lat, lng)
                if d > radius:
                    continue
                data['distance'] = round(d, 2)
            results.append(data)

        if lat and lng:
            results.sort(key=lambda x: x.get('distance') or 999)
        return Response({'count': len(results), 'results': results})

class ShopDetailView(generics.RetrieveAPIView):
    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopDetailSerializer
    permission_classes = [AllowAny]

class ShopProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        return Product.objects.filter(shop_id=self.kwargs['pk'], is_active=True)

# ─── Seller Dashboard ────────────────────────────────────────────────────────

class SellerShopsView(generics.ListCreateAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsSellerOrAdmin]
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.is_staff:
            return Shop.objects.all()
        if user.role == 'employee':
            return user.managed_shops.all()
        return Shop.objects.filter(owner=user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SellerShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsShopOwnerOrAdmin]
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.is_staff:
            return Shop.objects.all()
        if user.role == 'employee':
            return user.managed_shops.all()
        return Shop.objects.filter(owner=user)

class SellerProductsView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsSellerOrAdmin]
    def get_queryset(self):
        user = self.request.user
        shop_id = self.kwargs.get('shop_id')
        if shop_id:
            return Product.objects.filter(shop_id=shop_id)
        if user.role == 'admin':
            return Product.objects.all()
        if user.role == 'employee':
            return Product.objects.filter(shop__in=user.managed_shops.all())
        return Product.objects.filter(shop__owner=user)
    def perform_create(self, serializer):
        serializer.save()

class SellerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsShopOwnerOrAdmin]
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Product.objects.all()
        if user.role == 'employee':
            return Product.objects.filter(shop__in=user.managed_shops.all())
        return Product.objects.filter(shop__owner=user)

# ─── Reviews ─────────────────────────────────────────────────────────────────

class ReviewsView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    def get_queryset(self):
        shop_id = self.kwargs.get('shop_id')
        return Review.objects.filter(shop_id=shop_id, is_flagged=False)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, shop_id=self.kwargs['shop_id'])

# ─── Categories ──────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# ─── Admin Dashboard ─────────────────────────────────────────────────────────

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    def get(self, request):
        now = timezone.now()
        last_30 = now - timedelta(days=30)
        stats = {
            'total_users': User.objects.count(),
            'total_sellers': User.objects.filter(role='seller').count(),
            'total_customers': User.objects.filter(role='customer').count(),
            'total_employees': User.objects.filter(role='employee').count(),
            'total_shops': Shop.objects.count(),
            'verified_shops': Shop.objects.filter(is_verified=True).count(),
            'pending_shops': Shop.objects.filter(is_verified=False, is_active=True).count(),
            'total_products': Product.objects.count(),
            'total_reviews': Review.objects.count(),
            'flagged_reviews': Review.objects.filter(is_flagged=True).count(),
            'new_users_30d': User.objects.filter(created_at__gte=last_30).count(),
            'new_shops_30d': Shop.objects.filter(created_at__gte=last_30).count(),
        }
        return Response(stats)

class AdminUsersView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    def get_queryset(self):
        qs = User.objects.all().order_by('-created_at')
        role = self.request.GET.get('role')
        search = self.request.GET.get('search')
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search))
        return qs

class AdminUserActionView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        action = request.data.get('action')
        if action == 'verify':
            user.is_verified = True
        elif action == 'deactivate':
            user.is_active = False
        elif action == 'activate':
            user.is_active = True
        elif action == 'change_role':
            new_role = request.data.get('role')
            if new_role in ('customer', 'seller', 'employee', 'admin'):
                user.role = new_role
        user.save()
        return Response(AdminUserSerializer(user).data)

class AdminShopsView(generics.ListAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    def get_queryset(self):
        qs = Shop.objects.all().order_by('-created_at')
        status_filter = self.request.GET.get('status')
        search = self.request.GET.get('search')
        if status_filter == 'verified':
            qs = qs.filter(is_verified=True)
        elif status_filter == 'pending':
            qs = qs.filter(is_verified=False)
        elif status_filter == 'inactive':
            qs = qs.filter(is_active=False)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(owner__username__icontains=search))
        return qs

class AdminShopActionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    def patch(self, request, pk):
        try:
            shop = Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        action = request.data.get('action')
        if action == 'verify':
            shop.is_verified = True
        elif action == 'unverify':
            shop.is_verified = False
        elif action == 'deactivate':
            shop.is_active = False
        elif action == 'activate':
            shop.is_active = True
        shop.save()
        return Response(ShopSerializer(shop).data)

class AdminAssignEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def post(self, request, shop_id):
        try:
            shop = Shop.objects.get(pk=shop_id)
            user = User.objects.get(pk=request.data.get('user_id'))
        except (Shop.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'Not found'}, status=404)
        if user.role != 'employee':
            user.role = 'employee'
            user.save()
        shop.employees.add(user)
        return Response({'success': True})

class AdminReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    def get_queryset(self):
        qs = Review.objects.all().order_by('-created_at')
        if self.request.GET.get('flagged') == 'true':
            qs = qs.filter(is_flagged=True)
        return qs

class AdminReviewActionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    def delete(self, request, pk):
        try:
            Review.objects.get(pk=pk).delete()
        except Review.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        return Response(status=204)
    def patch(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        review.is_flagged = not review.is_flagged
        review.save()
        return Response(ReviewSerializer(review).data)
