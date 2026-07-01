from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from notifications.services import (
    send_tenant_visit_scheduled_notifications,
    send_verification_visit_scheduled_notifications,
)
from properties.models import Property
from visits.models import VisitQRToken, VisitRequest
from visits.serializers import VisitRequestSerializer
from visits.services import create_visit_request, find_same_city_agent


class VisitRequestViewSet(viewsets.ModelViewSet):
    serializer_class = VisitRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = VisitRequest.objects.select_related(
            "property",
            "tenant",
            "agent",
        ).prefetch_related("property__images")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(tenant=user)
        if user.role == User.Role.AGENT:
            return queryset.filter(agent=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(property__owner=user)
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can request visits.")
        serializer.instance = create_visit_request(
            tenant=self.request.user,
            **serializer.validated_data,
        )

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        visit = serializer.save()
        if (
            old_status != VisitRequest.Status.SCHEDULED
            and visit.status == VisitRequest.Status.SCHEDULED
            and visit.tenant.role == User.Role.TENANT
        ):
            self._schedule_tenant_visit(visit)

    def _schedule_tenant_visit(self, visit):
        update_fields = []
        if not visit.agent_id:
            visit.agent = find_same_city_agent(visit.property)
            update_fields.append("agent")
        if not visit.confirmed_slot:
            confirmed_slot = self._first_requested_slot(visit)
            if confirmed_slot:
                visit.confirmed_slot = confirmed_slot
                update_fields.append("confirmed_slot")
        if update_fields:
            update_fields.append("updated_at")
            visit.save(update_fields=update_fields)

        qr_token, created = VisitQRToken.objects.get_or_create(
            visit=visit,
            defaults={"expiry_time": timezone.now() + timedelta(hours=24)},
        )
        if not created and qr_token.expiry_time < timezone.now():
            qr_token.expiry_time = timezone.now() + timedelta(hours=24)
            qr_token.used_flag = False
            qr_token.save(update_fields=["expiry_time", "used_flag"])
        send_tenant_visit_scheduled_notifications(visit, qr_token)

    def _first_requested_slot(self, visit):
        requested_slot = next(
            (slot for slot in visit.requested_slots if isinstance(slot, str)),
            None,
        )
        if not requested_slot:
            return None
        parsed_slot = parse_datetime(requested_slot)
        if not parsed_slot:
            return None
        if timezone.is_naive(parsed_slot):
            return timezone.make_aware(parsed_slot)
        return parsed_slot

    @decorators.action(detail=False, methods=["post"], url_path="schedule-verification")
    def schedule_verification(self, request):
        if request.user.role != User.Role.AGENT:
            raise PermissionDenied("Only agents can schedule verification visits.")

        property_id = request.data.get("property")
        confirmed_slot = request.data.get("confirmed_slot")
        if not property_id or not confirmed_slot:
            return response.Response(
                {"detail": "Property and confirmed slot are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            property_obj = Property.objects.select_related("owner").get(
                id=property_id,
                status=Property.Status.PENDING,
            )
        except Property.DoesNotExist:
            return response.Response(
                {"detail": "Pending property was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.city and property_obj.city.lower() != request.user.city.lower():
            return response.Response(
                {"detail": "You can only schedule visits in your city."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(
            data={
                "property": property_obj.id,
                "agent": request.user.id,
                "tenant": property_obj.owner.id,
                "requested_slots": [confirmed_slot],
                "confirmed_slot": confirmed_slot,
                "status": VisitRequest.Status.SCHEDULED,
            }
        )
        serializer.is_valid(raise_exception=True)
        visit = VisitRequest.objects.create(
            property=property_obj,
            tenant=property_obj.owner,
            agent=request.user,
            requested_slots=[confirmed_slot],
            confirmed_slot=serializer.validated_data["confirmed_slot"],
            status=VisitRequest.Status.SCHEDULED,
        )
        qr_token = VisitQRToken.objects.create(
            visit=visit,
            expiry_time=timezone.now() + timedelta(hours=24),
        )
        send_verification_visit_scheduled_notifications(visit, qr_token)
        return response.Response(
            {
                **self.get_serializer(visit).data,
                "qr_token": qr_token.token_value,
            },
            status=status.HTTP_201_CREATED,
        )
