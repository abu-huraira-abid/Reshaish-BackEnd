from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from agreements.models import KeyHandover
from agreements.serializers import KeyHandoverSerializer
from agreements.services import confirm_key_handover


class KeyHandoverViewSet(viewsets.ModelViewSet):
    serializer_class = KeyHandoverSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = KeyHandover.objects.select_related("agreement")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(agreement__tenant=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(agreement__landlord=user)
        if user.role == User.Role.AGENT:
            return queryset
        return queryset.none()

    def perform_create(self, serializer):
        allowed_roles = [User.Role.LANDLORD, User.Role.AGENT, User.Role.ADMIN]
        if self.request.user.role not in allowed_roles:
            raise PermissionDenied(
                "Only landlords, agents, or admins can confirm handover."
            )
        serializer.instance = confirm_key_handover(
            confirmed_by=self.request.user,
            **serializer.validated_data,
        )
