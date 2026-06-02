from rest_framework import viewsets

from accounts.permissions import IsAdminRole
from payments.models import CommissionLedger
from payments.serializers import CommissionLedgerSerializer


class CommissionLedgerViewSet(viewsets.ModelViewSet):
    serializer_class = CommissionLedgerSerializer
    permission_classes = [IsAdminRole]
    queryset = CommissionLedger.objects.select_related("payment").all()
