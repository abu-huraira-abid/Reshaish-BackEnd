from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from visits.models import VisitRequest
from visits.serializers import VisitRequestSerializer
from visits.services import create_visit_request


class VisitRequestViewSet(viewsets.ModelViewSet):
    serializer_class = VisitRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = VisitRequest.objects.select_related("property", "tenant", "agent")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(tenant=user)
        if user.role == User.Role.AGENT:
            return queryset.filter(agent=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(property__owner=user)
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can request visits.")
        serializer.instance = create_visit_request(
            tenant=self.request.user,
            **serializer.validated_data,
        )
