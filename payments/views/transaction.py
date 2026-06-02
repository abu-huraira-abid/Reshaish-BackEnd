from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from payments.models import PaymentTransaction
from payments.serializers import PaymentTransactionSerializer
from payments.services import create_payment_transaction


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = PaymentTransaction.objects.select_related("agreement", "payer")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(payer=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(agreement__landlord=user)
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can create payment transactions.")
        serializer.instance = create_payment_transaction(
            payer=self.request.user,
            **serializer.validated_data,
        )
