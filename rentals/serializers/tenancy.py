from rest_framework import serializers

from rentals.models import RentalTenancy


class RentalTenancySerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source="property.title", read_only=True)
    property_address = serializers.CharField(source="property.address", read_only=True)
    property_city = serializers.CharField(source="property.city", read_only=True)
    property_image = serializers.SerializerMethodField()
    tenant_email = serializers.EmailField(source="tenant.email", read_only=True)
    landlord_email = serializers.EmailField(source="landlord.email", read_only=True)

    class Meta:
        model = RentalTenancy
        fields = [
            "id",
            "property",
            "property_title",
            "property_address",
            "property_city",
            "property_image",
            "agreement",
            "tenant",
            "tenant_email",
            "landlord",
            "landlord_email",
            "payment",
            "rent_amount",
            "security_deposit",
            "platform_fee",
            "agent_commission",
            "status",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_property_image(self, obj):
        image = obj.property.images.order_by("created_at").first()
        if not image:
            return ""
        request = self.context.get("request")
        url = image.image.url
        return request.build_absolute_uri(url) if request else url
