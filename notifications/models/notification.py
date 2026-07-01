from django.conf import settings
from django.db import models


class Notification(models.Model):
    class EventType(models.TextChoices):
        ONBOARDING_SUBMITTED = "onboarding_submitted", "Onboarding Submitted"
        PROPERTY_LISTED = "property_listed", "Property Listed"
        VERIFICATION_VISIT_SCHEDULED = (
            "verification_visit_scheduled",
            "Verification Visit Scheduled",
        )
        VERIFICATION_VISIT_CONFIRMED = (
            "verification_visit_confirmed",
            "Verification Visit Confirmed",
        )
        PROPERTY_STATUS_CHANGED = (
            "property_status_changed",
            "Property Status Changed",
        )
        TENANT_VISIT_REQUESTED = "tenant_visit_requested", "Tenant Visit Requested"
        TENANT_VISIT_SCHEDULED = "tenant_visit_scheduled", "Tenant Visit Scheduled"
        TENANT_VISIT_CONFIRMED = "tenant_visit_confirmed", "Tenant Visit Confirmed"
        RENTAL_PAYMENT_COMPLETED = (
            "rental_payment_completed",
            "Rental Payment Completed",
        )
        AGENT_COMMISSION_READY = "agent_commission_ready", "Agent Commission Ready"
        PROPERTY_ISSUE_REPORTED = (
            "property_issue_reported",
            "Property Issue Reported",
        )
        LEAVE_NOTICE_SUBMITTED = "leave_notice_submitted", "Leave Notice Submitted"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    event_type = models.CharField(max_length=80, choices=EventType.choices)
    title = models.CharField(max_length=160)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.recipient_id}"
