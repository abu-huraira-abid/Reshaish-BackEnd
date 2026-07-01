from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "actor",
            "actor_email",
            "event_type",
            "title",
            "message",
            "url",
            "metadata",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields
