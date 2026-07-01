import json

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from agreements.models import Agreement
from notifications.services import send_property_status_notifications
from properties.models import Property, PropertyImage
from properties.permissions import PropertyAccessPermission
from properties.serializers import PropertySerializer
from properties.services import create_property


class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [PropertyAccessPermission]
    filterset_fields = ["city", "property_type", "status"]
    search_fields = ["title", "address", "city", "description"]
    ordering_fields = ["rent", "created_at", "updated_at"]

    def get_available_queryset(self, queryset):
        reserved_statuses = [
            Agreement.Status.PENDING_ACCEPTANCE,
            Agreement.Status.PAYMENT_PENDING,
            Agreement.Status.ACTIVE,
        ]
        return queryset.filter(status=Property.Status.VERIFIED).exclude(
            agreement__status__in=reserved_statuses
        )

    def get_queryset(self):
        user = self.request.user
        queryset = Property.objects.select_related("owner").all()
        if not user.is_authenticated:
            return self.get_available_queryset(queryset)
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.LANDLORD:
            return queryset.filter(owner=user)
        if user.role == User.Role.AGENT:
            return queryset.filter(
                Q(status=Property.Status.PENDING) | Q(verification_reports__agent=user)
            ).distinct()
        available_queryset = self.get_available_queryset(queryset)
        if self.action == "retrieve" and user.role == User.Role.TENANT:
            return queryset.filter(
                Q(id__in=available_queryset.values("id"))
                | Q(
                    tenancies__tenant=user,
                    tenancies__status__in=["active", "notice_given"],
                )
                | Q(
                    agreement__tenant=user,
                    agreement__status__in=[
                        Agreement.Status.PENDING_ACCEPTANCE,
                        Agreement.Status.PAYMENT_PENDING,
                        Agreement.Status.ACTIVE,
                    ],
                )
            ).distinct()
        return available_queryset

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.LANDLORD:
            raise PermissionDenied("Only landlords can create property listings.")
        serializer.instance = create_property(
            owner=self.request.user,
            **serializer.validated_data,
        )
        PropertyImage.objects.bulk_create(
            PropertyImage(property=serializer.instance, image=image)
            for image in self.request.FILES.getlist("images")
        )

    def perform_update(self, serializer):
        if (
            self.request.user.role == User.Role.ADMIN
            and "status" in serializer.validated_data
            and serializer.validated_data["status"] != serializer.instance.status
        ):
            raise PermissionDenied(
                "Property approval and rejection is controlled by agent verification."
            )

        locked_statuses = [
            Agreement.Status.PAYMENT_PENDING,
            Agreement.Status.ACTIVE,
            Agreement.Status.ENDED,
        ]
        if (
            self.request.user.role == User.Role.LANDLORD
            and Agreement.objects.filter(
                property=serializer.instance,
                status__in=locked_statuses,
            ).exists()
        ):
            raise PermissionDenied(
                "This property cannot be edited after landlord acceptance."
            )

        old_status = serializer.instance.status
        serializer.save()
        new_status = serializer.instance.status
        if old_status != new_status:
            send_property_status_notifications(
                serializer.instance,
                self.request.user,
                old_status,
                new_status,
            )

        delete_image_ids = self.request.data.get("delete_image_ids")
        if delete_image_ids:
            try:
                delete_image_ids = json.loads(delete_image_ids)
            except (TypeError, ValueError):
                delete_image_ids = []
            queryset = serializer.instance.images.filter(id__in=delete_image_ids)
            for image in queryset:
                image.image.delete(save=False)
                image.delete()

        images = self.request.FILES.getlist("images")
        if images:
            PropertyImage.objects.bulk_create(
                PropertyImage(property=serializer.instance, image=image)
                for image in images
            )
