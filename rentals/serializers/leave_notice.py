from rest_framework import serializers

from rentals.models import LeaveNotice


class LeaveNoticeSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source="tenancy.property.title", read_only=True)
    submitted_by_email = serializers.EmailField(source="submitted_by.email", read_only=True)

    class Meta:
        model = LeaveNotice
        fields = [
            "id",
            "tenancy",
            "property_title",
            "submitted_by",
            "submitted_by_email",
            "notice_date",
            "move_out_date",
            "reason",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "submitted_by", "submitted_by_email", "created_at", "updated_at"]
