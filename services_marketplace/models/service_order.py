from django.conf import settings
from django.db import models


class ServiceOrder(models.Model):
    class ServiceType(models.TextChoices):
        MOVING = "moving", "Moving"
        TRANSPORT = "transport", "Transport"
        INTERNET = "internet", "Internet Setup"
        MAINTENANCE = "maintenance", "Maintenance"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    vendor_name = models.CharField(max_length=150, blank=True)
    schedule = models.DateTimeField()
    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    notes = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_type} order #{self.id}"
