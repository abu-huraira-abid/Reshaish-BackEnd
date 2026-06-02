from rest_framework import serializers

from visits.models import VisitQRToken


class VisitQRTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitQRToken
        fields = [
            "id",
            "visit",
            "token_value",
            "expiry_time",
            "used_flag",
            "created_at",
        ]
        read_only_fields = ["id", "token_value", "created_at"]
