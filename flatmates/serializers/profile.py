from rest_framework import serializers

from flatmates.models import FlatmateProfile


class FlatmateProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_photo = serializers.ImageField(source="user.profile_photo", read_only=True)

    class Meta:
        model = FlatmateProfile
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "user_photo",
            "city",
            "budget",
            "preferences",
            "match_visibility",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "user_photo",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email
