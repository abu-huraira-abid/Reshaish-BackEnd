from rest_framework import permissions, viewsets

from accounts.models import User
from visits.models import VisitQRToken
from visits.serializers import VisitQRTokenSerializer


class VisitQRTokenViewSet(viewsets.ModelViewSet):
    serializer_class = VisitQRTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = VisitQRToken.objects.select_related("visit", "visit__property")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.AGENT:
            return queryset.filter(visit__agent=user)
        if user.role == User.Role.TENANT:
            return queryset.filter(visit__tenant=user)
        return queryset.none()
