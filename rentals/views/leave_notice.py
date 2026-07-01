from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from rentals.models import LeaveNotice
from rentals.serializers import LeaveNoticeSerializer
from rentals.services import create_leave_notice_notifications


class LeaveNoticeViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveNoticeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = LeaveNotice.objects.select_related("tenancy", "tenancy__property", "submitted_by")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(tenancy__tenant=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(tenancy__landlord=user)
        return queryset.none()

    def perform_create(self, serializer):
        tenancy = serializer.validated_data["tenancy"]
        user = self.request.user
        if user.id not in [tenancy.tenant_id, tenancy.landlord_id]:
            raise PermissionDenied("Only tenant or landlord can submit leave notice.")
        notice = serializer.save(submitted_by=user)
        create_leave_notice_notifications(notice)
