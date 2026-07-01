from rest_framework import serializers

from visits.models import VisitRequest


class VisitRequestSerializer(serializers.ModelSerializer):
    property_detail = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()

    class Meta:
        model = VisitRequest
        fields = [
            "id",
            "property",
            "property_detail",
            "tenant",
            "tenant_name",
            "agent",
            "agent_name",
            "requested_slots",
            "confirmed_slot",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "property_detail",
            "tenant",
            "tenant_name",
            "agent_name",
            "created_at",
            "updated_at",
        ]

    def get_property_detail(self, obj):
        request = self.context.get("request")
        images = []
        for image in obj.property.images.all():
            if not image.image:
                continue
            url = image.image.url
            images.append(
                {
                    "id": image.id,
                    "url": request.build_absolute_uri(url) if request else url,
                }
            )
        return {
            "id": obj.property_id,
            "title": obj.property.title,
            "city": obj.property.city,
            "address": obj.property.address,
            "images": images,
        }

    def get_tenant_name(self, obj):
        return obj.tenant.get_full_name() or obj.tenant.email

    def get_agent_name(self, obj):
        if not obj.agent:
            return "Pending"
        return obj.agent.get_full_name() or obj.agent.email
