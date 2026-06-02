from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.services import create_user

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "role",
            "phone",
            "city",
        ]
        read_only_fields = ["id"]

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "Admin accounts must be created by an administrator."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        return create_user(password=password, **validated_data)
