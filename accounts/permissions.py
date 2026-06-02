from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "tenant"
        )


class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "landlord"
        )


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "agent"
        )


class IsAdminOrReadSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == "admin" or obj == request.user


class RolePermissionMixin:
    role_permissions = {}

    def get_permissions(self):
        permission_classes = self.role_permissions.get(
            self.action,
            self.permission_classes,
        )
        return [permission() for permission in permission_classes]
