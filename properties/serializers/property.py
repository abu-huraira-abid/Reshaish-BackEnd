from rest_framework import serializers

from properties.models import Property


class PropertySerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "owner",
            "owner_email",
            "title",
            "property_type",
            "address",
            "city",
            "rent",
            "deposit",
            "facilities",
            "rules",
            "description",
            "status",
            "ownership_proof",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]
