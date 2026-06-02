from rest_framework import permissions, viewsets

from accounts.models import User
from visits.models import VisitCheckIn
from visits.serializers import VisitCheckInSerializer


class VisitCheckInViewSet(viewsets.ModelViewSet):
    serializer_class = VisitCheckInSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = VisitCheckIn.objects.select_related("visit", "visit__property")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.AGENT:
            return queryset.filter(visit__agent=user)
        if user.role == User.Role.TENANT:
            return queryset.filter(visit__tenant=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(visit__property__owner=user)
        return queryset.none()
