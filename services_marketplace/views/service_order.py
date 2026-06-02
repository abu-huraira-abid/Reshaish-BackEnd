from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from services_marketplace.models import ServiceOrder
from services_marketplace.serializers import ServiceOrderSerializer
from services_marketplace.services import create_service_order


class ServiceOrderViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["service_type", "status"]
    ordering_fields = ["schedule", "created_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = ServiceOrder.objects.select_related("tenant", "property")
        if user.role in [User.Role.ADMIN, User.Role.AGENT]:
            return queryset
        return queryset.filter(tenant=user)

    def perform_create(self, serializer):
        if self.request.user.role not in [User.Role.TENANT, User.Role.LANDLORD]:
            raise PermissionDenied("Only tenants or landlords can book services.")
        serializer.instance = create_service_order(
            tenant=self.request.user,
            **serializer.validated_data,
        )
