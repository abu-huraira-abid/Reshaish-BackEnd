from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class CanCreateProperty(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.LANDLORD


class CanSubmitVerification(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.AGENT,
            User.Role.ADMIN,
        ]


class PropertyAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if view.action == "create":
            return (
                request.user.is_authenticated
                and request.user.role == User.Role.LANDLORD
            )
        return request.user.is_authenticated
