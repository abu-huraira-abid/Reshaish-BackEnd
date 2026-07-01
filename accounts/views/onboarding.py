from django.utils import timezone
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User, UserOnboarding
from accounts.serializers import UserOnboardingSerializer
from accounts.services.onboarding_notifications import (
    send_onboarding_approved_email,
    send_onboarding_rejected_email,
)
from notifications.services import send_onboarding_submitted_notification


class UserOnboardingViewSet(viewsets.ModelViewSet):
    serializer_class = UserOnboardingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = UserOnboarding.objects.select_related("user").order_by("-updated_at")
        if user.role == User.Role.ADMIN:
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _ensure_admin(self):
        if self.request.user.role != User.Role.ADMIN:
            raise PermissionDenied("Only administrators can review onboarding.")

    @decorators.action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        self._ensure_admin()
        instance = self.get_object()
        instance.status = UserOnboarding.Status.APPROVED
        instance.cnic_verified = True
        instance.rejection_reason = ""
        instance.reviewed_at = timezone.now()
        instance.save(
            update_fields=[
                "status",
                "cnic_verified",
                "rejection_reason",
                "reviewed_at",
                "updated_at",
            ]
        )
        send_onboarding_approved_email(instance)
        return response.Response(self.get_serializer(instance).data)

    @decorators.action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        self._ensure_admin()
        reason = request.data.get("reason", "").strip()
        if not reason:
            return response.Response(
                {"detail": "Rejection reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = self.get_object()
        instance.status = UserOnboarding.Status.REJECTED
        instance.cnic_verified = False
        instance.rejection_reason = reason
        instance.reviewed_at = timezone.now()
        instance.save(
            update_fields=[
                "status",
                "cnic_verified",
                "rejection_reason",
                "reviewed_at",
                "updated_at",
            ]
        )
        send_onboarding_rejected_email(instance)
        return response.Response(self.get_serializer(instance).data)

    @decorators.action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        instance = UserOnboarding.objects.filter(user=request.user).first()

        if request.method == "GET":
            if not instance:
                return response.Response(None)
            serializer = self.get_serializer(instance)
            return response.Response(serializer.data)

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=request.method == "PATCH",
        )
        serializer.is_valid(raise_exception=True)
        onboarding = serializer.save(user=request.user)
        send_onboarding_submitted_notification(onboarding)
        return response.Response(serializer.data)
