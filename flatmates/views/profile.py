from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from flatmates.models import FlatmateProfile
from flatmates.serializers import FlatmateProfileSerializer
from flatmates.services import create_flatmate_profile


class FlatmateProfileViewSet(viewsets.ModelViewSet):
    serializer_class = FlatmateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["city", "match_visibility"]
    ordering_fields = ["budget", "created_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = FlatmateProfile.objects.select_related("user")
        if user.role == User.Role.ADMIN:
            return queryset
        return queryset.filter(match_visibility=True) | queryset.filter(user=user)

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can create flatmate profiles.")
        serializer.instance = create_flatmate_profile(
            user=self.request.user,
            **serializer.validated_data,
        )
