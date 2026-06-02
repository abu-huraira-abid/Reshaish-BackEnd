from rest_framework import serializers

from services_marketplace.models import ServiceOrder


class ServiceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrder
        fields = [
            "id",
            "tenant",
            "property",
            "service_type",
            "vendor_name",
            "schedule",
            "amount",
            "status",
            "notes",
            "rating",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]
