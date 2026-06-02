from rest_framework.permissions import BasePermission

from accounts.models import User


class CanBookService(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.TENANT,
            User.Role.LANDLORD,
        ]
