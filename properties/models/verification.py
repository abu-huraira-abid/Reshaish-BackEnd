from django.conf import settings
from django.db import models


class VerificationReport(models.Model):
    class Decision(models.TextChoices):
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        NEED_EVIDENCE = "need_evidence", "Need More Evidence"

    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.CASCADE,
        related_name="verification_reports",
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="verification_reports",
    )
    checklist = models.JSONField(default=dict)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to="verification_photos/", blank=True)
    decision = models.CharField(max_length=20, choices=Decision.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property} - {self.decision}"
