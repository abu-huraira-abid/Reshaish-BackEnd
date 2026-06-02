from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from properties.models import VerificationReport
from properties.serializers import VerificationReportSerializer
from properties.services import create_verification_report


class VerificationReportViewSet(viewsets.ModelViewSet):
    serializer_class = VerificationReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = VerificationReport.objects.select_related("property", "agent")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.AGENT:
            return queryset.filter(agent=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(property__owner=user)
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role not in [User.Role.AGENT, User.Role.ADMIN]:
            raise PermissionDenied(
                "Only agents or admins can submit verification reports."
            )
        serializer.instance = create_verification_report(
            agent=self.request.user,
            **serializer.validated_data,
        )
