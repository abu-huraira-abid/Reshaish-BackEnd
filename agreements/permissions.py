from rest_framework.permissions import BasePermission

from accounts.models import User


class CanCreateAgreement(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.LANDLORD,
            User.Role.ADMIN,
        ]


class CanConfirmKeyHandover(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.LANDLORD,
            User.Role.AGENT,
            User.Role.ADMIN,
        ]
