from rest_framework import serializers

from payments.models import PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    total_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "agreement",
            "payer",
            "amount_breakdown",
            "gateway_ref",
            "status",
            "total_amount",
            "created_at",
        ]
        read_only_fields = ["id", "payer", "created_at"]
