from rest_framework.permissions import BasePermission

from accounts.models import User


class CanCreateFlatmateProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TENANT
