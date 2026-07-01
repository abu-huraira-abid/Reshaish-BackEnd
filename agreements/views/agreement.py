from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from agreements.models import Agreement
from agreements.serializers import AgreementSerializer
from agreements.services import create_agreement


class AgreementViewSet(viewsets.ModelViewSet):
    serializer_class = AgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Agreement.objects.select_related(
            "property", "tenant", "landlord"
        ).order_by("-updated_at", "-created_at", "-id")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(tenant=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(landlord=user)
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role == User.Role.TENANT:
            property_obj = serializer.validated_data.get("property")
            if not property_obj:
                raise PermissionDenied("Property is required for rental intent.")
            serializer.validated_data["tenant"] = self.request.user
            serializer.validated_data["landlord"] = property_obj.owner
            serializer.validated_data["status"] = Agreement.Status.PENDING_ACCEPTANCE
        elif self.request.user.role not in [User.Role.LANDLORD, User.Role.ADMIN]:
            raise PermissionDenied("Only tenants, landlords, or admins can create agreements.")
        serializer.instance = create_agreement(**serializer.validated_data)
