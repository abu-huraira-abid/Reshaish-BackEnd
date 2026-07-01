from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from notifications.models import Notification
from notifications.services import notify_admins, notify_user
from rentals.models import PropertyIssue
from rentals.serializers import PropertyIssueSerializer
from rentals.services import create_issue_notifications


class PropertyIssueViewSet(viewsets.ModelViewSet):
    serializer_class = PropertyIssueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = PropertyIssue.objects.select_related("tenancy", "tenancy__property", "reported_by")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(tenancy__tenant=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(tenancy__landlord=user)
        return queryset.none()

    def perform_create(self, serializer):
        tenancy = serializer.validated_data["tenancy"]
        if self.request.user.role != User.Role.TENANT or tenancy.tenant_id != self.request.user.id:
            raise PermissionDenied("Only the tenant can report issues for this tenancy.")
        issue = serializer.save(reported_by=self.request.user)
        create_issue_notifications(issue)

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        issue = serializer.save()
        if old_status != issue.status:
            message = (
                f"{issue.title} for {issue.tenancy.property.title} changed "
                f"from {old_status} to {issue.status}."
            )
            notify_user(
                recipient=issue.tenancy.tenant,
                actor=self.request.user,
                event_type=Notification.EventType.PROPERTY_ISSUE_REPORTED,
                title="Property issue status updated",
                message=message,
                url="/tenant/property-history",
                metadata={"issue_id": issue.id, "tenancy_id": issue.tenancy_id},
            )
            notify_admins(
                actor=self.request.user,
                event_type=Notification.EventType.PROPERTY_ISSUE_REPORTED,
                title="Property issue status updated",
                message=message,
                url="/admin/audit",
                metadata={"issue_id": issue.id, "tenancy_id": issue.tenancy_id},
            )
