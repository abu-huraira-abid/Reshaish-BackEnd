from django.conf import settings
from django.db import models


class Property(models.Model):
    class PropertyType(models.TextChoices):
        HOUSE = "house", "House"
        APARTMENT = "apartment", "Apartment"
        ROOM = "room", "Room"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending_verification", "Pending Verification"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        UNAVAILABLE = "unavailable", "Unavailable"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="properties",
    )
    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    address = models.TextField()
    city = models.CharField(max_length=100)
    rent = models.PositiveIntegerField()
    deposit = models.PositiveIntegerField(default=0)
    facilities = models.JSONField(default=list, blank=True)
    rules = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    ownership_proof = models.FileField(upload_to="ownership_proofs/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
