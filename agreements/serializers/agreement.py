from rest_framework import serializers

from agreements.models import Agreement


class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = [
            "id",
            "property",
            "tenant",
            "landlord",
            "terms",
            "pdf",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
