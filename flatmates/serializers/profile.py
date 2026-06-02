from rest_framework import serializers

from flatmates.models import FlatmateProfile


class FlatmateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatmateProfile
        fields = [
            "id",
            "user",
            "city",
            "budget",
            "preferences",
            "match_visibility",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
