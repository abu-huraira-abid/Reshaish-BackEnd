from rest_framework import serializers

from properties.models import VerificationReport


class VerificationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationReport
        fields = [
            "id",
            "property",
            "agent",
            "checklist",
            "notes",
            "photo",
            "decision",
            "created_at",
        ]
        read_only_fields = ["id", "agent", "created_at"]
