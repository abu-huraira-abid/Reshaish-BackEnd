from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from flatmates.models import FlatmateListing
from flatmates.serializers import FlatmateListingSerializer
from flatmates.services import create_flatmate_listing


class FlatmateListingViewSet(viewsets.ModelViewSet):
    serializer_class = FlatmateListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "tenancy__property__city"]
    ordering_fields = ["expected_share", "created_at", "updated_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = FlatmateListing.objects.select_related(
            "created_by",
            "tenancy",
            "tenancy__property",
        )
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(
                Q(status=FlatmateListing.Status.ACTIVE) | Q(created_by=user)
            )
        return queryset.filter(status=FlatmateListing.Status.ACTIVE)

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can list a rental for flatmates.")
        serializer.instance = create_flatmate_listing(
            user=self.request.user,
            **serializer.validated_data,
        )

    def perform_update(self, serializer):
        if (
            self.request.user.role != User.Role.ADMIN
            and serializer.instance.created_by_id != self.request.user.id
        ):
            raise PermissionDenied("You can only update your own flatmate listing.")
        serializer.instance = create_flatmate_listing(
            user=serializer.instance.created_by,
            **{**serializer.validated_data, "tenancy": serializer.instance.tenancy},
        )
