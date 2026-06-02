from rest_framework import serializers

from visits.models import VisitCheckIn


class VisitCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitCheckIn
        fields = [
            "id",
            "visit",
            "tenant_scan_time",
            "agent_scan_time",
            "checkout_time",
            "location",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
