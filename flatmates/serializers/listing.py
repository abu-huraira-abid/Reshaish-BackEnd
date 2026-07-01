from rest_framework import serializers

from flatmates.models import FlatmateListing


class FlatmateListingSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.EmailField(source="created_by.email", read_only=True)
    owner_photo = serializers.ImageField(source="created_by.profile_photo", read_only=True)
    property = serializers.IntegerField(source="tenancy.property_id", read_only=True)
    property_title = serializers.CharField(source="tenancy.property.title", read_only=True)
    property_address = serializers.CharField(source="tenancy.property.address", read_only=True)
    property_city = serializers.CharField(source="tenancy.property.city", read_only=True)
    rent_amount = serializers.IntegerField(source="tenancy.rent_amount", read_only=True)

    class Meta:
        model = FlatmateListing
        fields = [
            "id",
            "tenancy",
            "created_by",
            "owner_name",
            "owner_email",
            "owner_photo",
            "property",
            "property_title",
            "property_address",
            "property_city",
            "rent_amount",
            "title",
            "available_room",
            "expected_share",
            "available_from",
            "house_rules",
            "preferences",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "owner_name",
            "owner_email",
            "owner_photo",
            "property",
            "property_title",
            "property_address",
            "property_city",
            "rent_amount",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "tenancy": {"validators": []},
        }

    def get_owner_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.email
