from rest_framework import serializers

from payments.models import CommissionLedger


class CommissionLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionLedger
        fields = [
            "id",
            "payment",
            "rule",
            "commission_amount",
            "settlement_amount",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
