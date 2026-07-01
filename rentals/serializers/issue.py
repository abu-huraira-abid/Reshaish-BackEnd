from rest_framework import serializers

from rentals.models import PropertyIssue


class PropertyIssueSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source="tenancy.property.title", read_only=True)
    reported_by_email = serializers.EmailField(source="reported_by.email", read_only=True)

    class Meta:
        model = PropertyIssue
        fields = [
            "id",
            "tenancy",
            "property_title",
            "reported_by",
            "reported_by_email",
            "title",
            "description",
            "priority",
            "status",
            "resolution_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reported_by", "reported_by_email", "created_at", "updated_at"]
