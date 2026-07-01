from django.utils import timezone
from rest_framework import decorators, permissions, response, status, viewsets

from accounts.models import User
from notifications.services import (
    send_tenant_visit_confirmed_notifications,
    send_verification_visit_confirmed_notifications,
)
from visits.models import VisitCheckIn, VisitQRToken, VisitRequest
from visits.serializers import VisitQRTokenSerializer


class VisitQRTokenViewSet(viewsets.ModelViewSet):
    serializer_class = VisitQRTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = VisitQRToken.objects.select_related("visit", "visit__property")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.AGENT:
            return queryset.filter(visit__agent=user)
        if user.role == User.Role.TENANT:
            return queryset.filter(visit__tenant=user)
        return queryset.none()

    def create(self, request, *args, **kwargs):
        visit_id = request.data.get("visit")
        expiry_time = request.data.get("expiry_time")
        if not visit_id or not expiry_time:
            return response.Response(
                {"detail": "Visit and expiry time are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            visit = VisitRequest.objects.select_related("tenant", "agent").get(
                id=visit_id,
            )
        except VisitRequest.DoesNotExist:
            return response.Response(
                {"detail": "Visit was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == User.Role.TENANT and visit.tenant_id != request.user.id:
            return response.Response(
                {"detail": "You can only generate QR codes for your visits."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role == User.Role.AGENT and visit.agent_id != request.user.id:
            return response.Response(
                {"detail": "You can only generate QR codes for assigned visits."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role not in [User.Role.ADMIN, User.Role.AGENT, User.Role.TENANT]:
            return response.Response(
                {"detail": "You cannot generate QR codes for this visit."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, created = VisitQRToken.objects.get_or_create(
            visit=visit,
            defaults={"expiry_time": serializer.validated_data["expiry_time"]},
        )
        if not created and token.expiry_time < timezone.now():
            token.expiry_time = serializer.validated_data["expiry_time"]
            token.used_flag = False
            token.save(update_fields=["expiry_time", "used_flag"])
        return response.Response(
            self.get_serializer(token).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @decorators.action(detail=False, methods=["post"], url_path="scan")
    def scan(self, request):
        if request.user.role != User.Role.AGENT:
            return response.Response(
                {"detail": "Only agents can scan visit QR codes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token_value = request.data.get("token")
        if not token_value:
            return response.Response(
                {"detail": "QR token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = VisitQRToken.objects.select_related(
                "visit",
                "visit__property",
                "visit__property__owner",
                "visit__agent",
                "visit__tenant",
            ).get(token_value=token_value)
        except VisitQRToken.DoesNotExist:
            return response.Response(
                {"detail": "Invalid QR token."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if token.visit.agent_id != request.user.id:
            return response.Response(
                {"detail": "This QR code is assigned to another agent."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if token.used_flag:
            return response.Response(
                {"detail": "This QR code was already used."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if token.expiry_time < timezone.now():
            return response.Response(
                {"detail": "This QR code has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token.used_flag = True
        token.save(update_fields=["used_flag"])
        visit = token.visit
        visit.status = VisitRequest.Status.CHECKED_IN
        visit.save(update_fields=["status", "updated_at"])
        checkin, _ = VisitCheckIn.objects.get_or_create(visit=visit)
        checkin.agent_scan_time = timezone.now()
        checkin.save(update_fields=["agent_scan_time"])
        if visit.tenant.role == User.Role.TENANT:
            send_tenant_visit_confirmed_notifications(visit, request.user)
            detail = "Tenant visit confirmed."
        else:
            send_verification_visit_confirmed_notifications(visit, request.user)
            detail = "Verification visit confirmed."

        return response.Response(
            {
                "detail": detail,
                "visit": visit.id,
                "property": visit.property_id,
            }
        )
