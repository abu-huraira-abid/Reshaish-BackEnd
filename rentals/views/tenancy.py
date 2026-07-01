from rest_framework import permissions, viewsets

from accounts.models import User
from rentals.models import RentalTenancy
from rentals.serializers import RentalTenancySerializer


class RentalTenancyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RentalTenancySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = RentalTenancy.objects.select_related("property", "tenant", "landlord", "agreement", "payment")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(tenant=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(landlord=user)
        return queryset.none()
