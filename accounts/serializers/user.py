from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers.auth import PASSWORD_MESSAGE, PASSWORD_PATTERN

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "phone",
            "city",
            "profile_photo",
            "email_verified",
            "is_active",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "role",
            "email_verified",
            "is_active",
            "date_joined",
            "last_login",
        ]

    def validate_email(self, value):
        email = value.strip().lower()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("This email is already registered.")
        return email

    def validate_phone(self, value):
        phone = value.strip()
        if not phone:
            return phone

        queryset = User.objects.filter(phone=phone)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "This phone number is already registered."
            )
        return phone


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        if not PASSWORD_PATTERN.match(value):
            raise serializers.ValidationError(PASSWORD_MESSAGE)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
