from rest_framework import serializers

from visits.models import VisitRequest


class VisitRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitRequest
        fields = [
            "id",
            "property",
            "tenant",
            "agent",
            "requested_slots",
            "confirmed_slot",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]
