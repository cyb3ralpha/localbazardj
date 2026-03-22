from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ('admin', 'employee') or request.user.is_staff
        )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )

class IsSellerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('seller', 'admin', 'employee')

class IsShopOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role == 'admin' or user.is_staff:
            return True
        if user.role == 'employee':
            from shops.models import Shop
            shop = obj if isinstance(obj, Shop) else getattr(obj, 'shop', None)
            return shop and shop in user.managed_shops.all()
        return getattr(obj, 'owner', None) == user or getattr(getattr(obj, 'shop', None), 'owner', None) == user
