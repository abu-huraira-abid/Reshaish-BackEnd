from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import (
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    SendEmailOTPSerializer,
    UserSerializer,
    VerifyEmailOTPSerializer,
)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh") or request.data.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                return Response(
                    {"detail": "Invalid refresh token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SendEmailOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendEmailOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        latest_otp = user.email_otps.order_by("-created_at").first()
        return Response(
            {
                "detail": "Verification code sent.",
                "expires_at": latest_otp.expires_at if latest_otp else None,
                "expires_in_seconds": 60
                * getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10),
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            {
                "detail": "Email verified successfully.",
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            status=status.HTTP_200_OK,
        )
