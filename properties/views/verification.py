from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from properties.models import VerificationReport
from properties.serializers import VerificationReportSerializer
from properties.services import create_verification_report
from visits.models import VisitRequest


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
        property_obj = serializer.validated_data["property"]
        if self.request.user.role == User.Role.AGENT:
            has_confirmed_visit = VisitRequest.objects.filter(
                property=property_obj,
                agent=self.request.user,
                status__in=[
                    VisitRequest.Status.CHECKED_IN,
                    VisitRequest.Status.COMPLETED,
                ],
            ).exists()
            if not has_confirmed_visit:
                raise PermissionDenied(
                    "Schedule and confirm the verification visit before submitting "
                    "a report."
                )
        serializer.instance = create_verification_report(
            agent=self.request.user,
            **serializer.validated_data,
        )
