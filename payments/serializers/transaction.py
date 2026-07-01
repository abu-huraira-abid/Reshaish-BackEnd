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
            "currency",
            "stripe_checkout_session_id",
            "stripe_payment_intent_id",
            "status",
            "total_amount",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "payer",
            "currency",
            "stripe_checkout_session_id",
            "stripe_payment_intent_id",
            "created_at",
        ]
