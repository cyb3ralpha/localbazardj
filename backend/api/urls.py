from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/profile/', views.ProfileView.as_view()),

    # Public
    path('search/', views.search_products),
    path('shops/nearby/', views.NearbyShopsView.as_view()),
    path('shops/<int:pk>/', views.ShopDetailView.as_view()),
    path('shops/<int:pk>/products/', views.ShopProductsView.as_view()),
    path('shops/<int:shop_id>/reviews/', views.ReviewsView.as_view()),
    path('categories/', views.CategoryListView.as_view()),

    # Seller
    path('seller/shops/', views.SellerShopsView.as_view()),
    path('seller/shops/<int:pk>/', views.SellerShopDetailView.as_view()),
    path('seller/shops/<int:shop_id>/products/', views.SellerProductsView.as_view()),
    path('seller/products/', views.SellerProductsView.as_view()),
    path('seller/products/<int:pk>/', views.SellerProductDetailView.as_view()),

    # Admin
    path('admin/stats/', views.AdminStatsView.as_view()),
    path('admin/users/', views.AdminUsersView.as_view()),
    path('admin/users/<int:pk>/action/', views.AdminUserActionView.as_view()),
    path('admin/shops/', views.AdminShopsView.as_view()),
    path('admin/shops/<int:pk>/action/', views.AdminShopActionView.as_view()),
    path('admin/shops/<int:shop_id>/assign-employee/', views.AdminAssignEmployeeView.as_view()),
    path('admin/reviews/', views.AdminReviewsView.as_view()),
    path('admin/reviews/<int:pk>/', views.AdminReviewActionView.as_view()),
]
