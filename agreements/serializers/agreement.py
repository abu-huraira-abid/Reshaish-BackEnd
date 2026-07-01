from rest_framework import serializers

from agreements.models import Agreement


class AgreementSerializer(serializers.ModelSerializer):
    property_detail = serializers.SerializerMethodField()
    tenant_detail = serializers.SerializerMethodField()
    landlord_detail = serializers.SerializerMethodField()

    class Meta:
        model = Agreement
        fields = [
            "id",
            "property",
            "property_detail",
            "tenant",
            "tenant_detail",
            "landlord",
            "landlord_detail",
            "terms",
            "pdf",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "property_detail",
            "tenant_detail",
            "landlord_detail",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "tenant": {"required": False},
            "landlord": {"required": False},
            "status": {"required": False},
        }

    def get_property_detail(self, obj):
        return {
            "id": obj.property_id,
            "title": obj.property.title,
            "address": obj.property.address,
            "city": obj.property.city,
            "rent": obj.property.rent,
            "deposit": obj.property.deposit,
        }

    def get_tenant_detail(self, obj):
        return {
            "id": obj.tenant_id,
            "name": obj.tenant.get_full_name() or obj.tenant.email,
            "email": obj.tenant.email,
            "phone": obj.tenant.phone,
        }

    def get_landlord_detail(self, obj):
        return {
            "id": obj.landlord_id,
            "name": obj.landlord.get_full_name() or obj.landlord.email,
            "email": obj.landlord.email,
            "phone": obj.landlord.phone,
        }
