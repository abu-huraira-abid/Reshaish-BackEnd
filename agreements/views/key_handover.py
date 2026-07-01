from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from agreements.models import Agreement, KeyHandover
from agreements.serializers import KeyHandoverSerializer
from agreements.services import (
    confirm_key_handover,
    get_tenant_property_agreement,
    send_key_handover_otp,
    verify_key_handover_otp,
)


class KeyHandoverViewSet(viewsets.ModelViewSet):
    serializer_class = KeyHandoverSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = KeyHandover.objects.select_related("agreement")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(agreement__tenant=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(agreement__landlord=user)
        if user.role == User.Role.AGENT:
            return queryset
        return queryset.none()

    def perform_create(self, serializer):
        allowed_roles = [User.Role.LANDLORD, User.Role.AGENT, User.Role.ADMIN]
        if self.request.user.role not in allowed_roles:
            raise PermissionDenied(
                "Only landlords, agents, or admins can confirm handover."
            )
        serializer.instance = confirm_key_handover(
            confirmed_by=self.request.user,
            **serializer.validated_data,
        )

    @decorators.action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
        if request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can start key handover.")
        property_id = request.data.get("property") or request.data.get("property_id")
        if not property_id:
            return response.Response(
                {"detail": "Property is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        agreement = get_tenant_property_agreement(
            tenant=request.user,
            property_id=property_id,
        )
        if not agreement:
            return response.Response(
                {
                    "detail": (
                        "Key handover is available after the agreement is active "
                        "and payment is completed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if hasattr(agreement, "key_handover"):
            return response.Response(
                {
                    "detail": "Key handover is already complete.",
                    "agreement": agreement.id,
                    "completed": True,
                }
            )
        expires_at = send_key_handover_otp(agreement)
        qr_payload = (
            f"rehaish://key-handover?"
            f"agreement={agreement.id}&property={agreement.property_id}"
        )
        return response.Response(
            {
                "agreement": agreement.id,
                "agreement_number": f"AGR-{agreement.id:06d}",
                "expires_at": expires_at,
                "qr_payload": qr_payload,
                "tenant_email": request.user.email,
            }
        )

    @decorators.action(detail=False, methods=["post"], url_path="qr")
    def qr(self, request):
        if request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can create key handover QR codes.")
        property_id = request.data.get("property") or request.data.get("property_id")
        if not property_id:
            return response.Response(
                {"detail": "Property is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        agreement = get_tenant_property_agreement(
            tenant=request.user,
            property_id=property_id,
        )
        if not agreement:
            return response.Response(
                {
                    "detail": (
                        "Key handover QR is available after the agreement is active "
                        "and payment is completed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        qr_payload = (
            f"rehaish://key-handover?"
            f"agreement={agreement.id}&property={agreement.property_id}"
        )
        return response.Response(
            {
                "agreement": agreement.id,
                "agreement_number": f"AGR-{agreement.id:06d}",
                "qr_payload": qr_payload,
                "tenant_email": request.user.email,
            }
        )

    @decorators.action(detail=False, methods=["post"], url_path="scan")
    def scan(self, request):
        allowed_roles = [User.Role.AGENT, User.Role.LANDLORD, User.Role.ADMIN]
        if request.user.role not in allowed_roles:
            raise PermissionDenied("Only agents, landlords, or admins can scan handover QR codes.")

        agreement_id = request.data.get("agreement")
        property_id = request.data.get("property") or request.data.get("property_id")
        if not agreement_id or not property_id:
            return response.Response(
                {"detail": "Agreement and property are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agreement = (
            self.get_queryset()
            .filter(agreement_id=agreement_id, agreement__property_id=property_id)
            .select_related("agreement", "agreement__tenant", "agreement__property")
            .first()
        )
        if agreement:
            return response.Response(
                {"detail": "Key handover is already complete.", "completed": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agreement = (
            Agreement.objects.select_related("tenant", "landlord", "property")
            .filter(id=agreement_id, property_id=property_id)
            .first()
        )
        if not agreement:
            return response.Response(
                {"detail": "Agreement was not found for this QR code."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user.role == User.Role.LANDLORD and agreement.landlord_id != request.user.id:
            return response.Response(
                {"detail": "This handover is assigned to another landlord."},
                status=status.HTTP_403_FORBIDDEN,
            )

        expires_at = send_key_handover_otp(agreement)
        return response.Response(
            {
                "detail": "Handover QR scanned. OTP sent to tenant email.",
                "agreement": agreement.id,
                "agreement_number": f"AGR-{agreement.id:06d}",
                "property": agreement.property_id,
                "property_title": agreement.property.title,
                "tenant_email": agreement.tenant.email,
                "expires_at": expires_at,
            }
        )

    @decorators.action(detail=False, methods=["post"], url_path="verify-otp")
    def verify_otp(self, request):
        if request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can verify key handover OTP.")
        property_id = request.data.get("property") or request.data.get("property_id")
        code = request.data.get("code")
        if not property_id or not code:
            return response.Response(
                {"detail": "Property and OTP code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        agreement = get_tenant_property_agreement(
            tenant=request.user,
            property_id=property_id,
        )
        if not agreement:
            return response.Response(
                {
                    "detail": (
                        "Key handover is available after the agreement is active "
                        "and payment is completed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        handover, error = verify_key_handover_otp(
            agreement=agreement,
            code=code,
            confirmed_by=request.user,
            notes=request.data.get("notes", ""),
        )
        if error:
            return response.Response(
                {"detail": error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return response.Response(self.get_serializer(handover).data)
