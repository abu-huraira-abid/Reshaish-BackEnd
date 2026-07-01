import re

from rest_framework import serializers

from accounts.models import UserOnboarding

CNIC_PATTERN = re.compile(r"^\d{5}-\d{7}-\d$|^\d{13}$")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


class UserOnboardingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = UserOnboarding
        fields = [
            "id",
            "user",
            "user_email",
            "role",
            "cnic_number",
            "cnic_front_image",
            "cnic_back_image",
            "date_of_birth",
            "gender",
            "current_address",
            "occupation",
            "emergency_contact_name",
            "emergency_contact_phone",
            "status",
            "cnic_format_valid",
            "cnic_images_present",
            "cnic_verified",
            "rejection_reason",
            "submitted_at",
            "updated_at",
            "reviewed_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "role",
            "status",
            "cnic_format_valid",
            "cnic_images_present",
            "cnic_verified",
            "rejection_reason",
            "submitted_at",
            "updated_at",
            "reviewed_at",
        ]

    def validate_cnic_number(self, value):
        normalized = value.strip()
        if not CNIC_PATTERN.match(normalized):
            raise serializers.ValidationError(
                "Enter a valid CNIC, for example 12345-1234567-1."
            )
        return normalized

    def validate_cnic_front_image(self, value):
        return self._validate_cnic_image(value)

    def validate_cnic_back_image(self, value):
        return self._validate_cnic_image(value)

    def _validate_cnic_image(self, value):
        if value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError("CNIC image must be 5MB or smaller.")
        content_type = getattr(value, "content_type", "")
        if content_type and content_type not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Upload a JPG, PNG, or WebP image.")
        return value

    def validate(self, attrs):
        front = attrs.get("cnic_front_image") or getattr(
            self.instance, "cnic_front_image", None
        )
        back = attrs.get("cnic_back_image") or getattr(
            self.instance, "cnic_back_image", None
        )
        if not front or not back:
            raise serializers.ValidationError(
                "Both CNIC front and back images are required."
            )
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["cnic_format_valid"] = True
        validated_data["cnic_images_present"] = True
        validated_data["status"] = UserOnboarding.Status.PENDING
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["cnic_format_valid"] = True
        validated_data["cnic_images_present"] = True
        validated_data["status"] = UserOnboarding.Status.PENDING
        validated_data["cnic_verified"] = False
        validated_data["rejection_reason"] = ""
        return super().update(instance, validated_data)
