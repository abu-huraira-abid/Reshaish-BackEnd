from django.conf import settings
from django.db import models


class FlatmateListing(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CLOSED = "closed", "Closed"

    tenancy = models.OneToOneField(
        "rentals.RentalTenancy",
        on_delete=models.CASCADE,
        related_name="flatmate_listing",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flatmate_listings",
    )
    title = models.CharField(max_length=200)
    available_room = models.CharField(max_length=120, blank=True)
    expected_share = models.PositiveIntegerField(default=0)
    available_from = models.DateField(null=True, blank=True)
    house_rules = models.JSONField(default=list, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.tenancy.property.title})"
