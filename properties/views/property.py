from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from properties.models import Property
from properties.permissions import PropertyAccessPermission
from properties.serializers import PropertySerializer
from properties.services import create_property


class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [PropertyAccessPermission]
    filterset_fields = ["city", "property_type", "status"]
    search_fields = ["title", "address", "city", "description"]
    ordering_fields = ["rent", "created_at", "updated_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = Property.objects.select_related("owner").all()
        if not user.is_authenticated:
            return queryset.filter(status=Property.Status.VERIFIED)
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.LANDLORD:
            return queryset.filter(owner=user)
        if user.role == User.Role.AGENT:
            return queryset.filter(
                Q(status=Property.Status.PENDING) | Q(verification_reports__agent=user)
            ).distinct()
        return queryset.filter(status=Property.Status.VERIFIED)

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.LANDLORD:
            raise PermissionDenied("Only landlords can create property listings.")
        serializer.instance = create_property(
            owner=self.request.user,
            **serializer.validated_data,
        )
