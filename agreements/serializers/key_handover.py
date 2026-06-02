from rest_framework import serializers

from agreements.models import KeyHandover


class KeyHandoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyHandover
        fields = [
            "id",
            "agreement",
            "method",
            "proof",
            "confirmed_by",
            "timestamp",
            "notes",
        ]
        read_only_fields = ["id", "confirmed_by", "timestamp"]
