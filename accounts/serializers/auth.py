import re

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import EmailOTP
from accounts.services import create_user
from accounts.services.email_verification import send_email_verification_otp

User = get_user_model()
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
PASSWORD_MESSAGE = (
    "Password must be at least 8 characters and include one uppercase letter, "
    "one number, and one symbol."
)


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

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email

    def validate_phone(self, value):
        phone = value.strip()
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                "This phone number is already registered."
            )
        return phone

    def validate_username(self, value):
        username = value.strip().lower()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("This username is already registered.")
        return username

    def validate_password(self, value):
        if not PASSWORD_PATTERN.match(value):
            raise serializers.ValidationError(PASSWORD_MESSAGE)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = create_user(password=password, **validated_data)
        send_email_verification_otp(user)
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.email_verified:
            raise serializers.ValidationError(
                {
                    "detail": "Please verify your email before logging in.",
                    "code": "email_not_verified",
                    "email": self.user.email,
                }
            )
        return data


class SendEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            return User.objects.get(email__iexact=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError(
                "No account found for this email."
            ) from exc

    def save(self, **kwargs):
        user = self.validated_data["email"]
        send_email_verification_otp(user)
        return user


class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        try:
            user = User.objects.get(email__iexact=attrs["email"])
        except User.DoesNotExist as exc:
            raise serializers.ValidationError(
                "No account found for this email."
            ) from exc

        otp = (
            EmailOTP.objects.filter(
                user=user,
                purpose=EmailOTP.Purpose.VERIFY_EMAIL,
                consumed_at__isnull=True,
            )
            .order_by("-created_at")
            .first()
        )
        if not otp:
            raise serializers.ValidationError("No active verification code found.")
        if otp.is_expired:
            raise serializers.ValidationError("Verification code has expired.")
        if otp.attempts >= 5:
            raise serializers.ValidationError("Too many attempts. Request a new code.")
        if not otp.check_code(attrs["code"]):
            raise serializers.ValidationError("Invalid verification code.")

        attrs["user"] = user
        attrs["otp"] = otp
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]
        otp.consume()
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "verified_at": timezone.now(),
        }
