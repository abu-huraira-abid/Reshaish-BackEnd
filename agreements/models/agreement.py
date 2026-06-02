from django.conf import settings
from django.db import models


class Agreement(models.Model):
    class Status(models.TextChoices):
        GENERATED = "generated", "Generated"
        PENDING_ACCEPTANCE = "pending_acceptance", "Pending Acceptance"
        PAYMENT_PENDING = "payment_pending", "Payment Pending"
        ACTIVE = "active", "Active"
        ENDED = "ended", "Ended"
        CANCELLED = "cancelled", "Cancelled"

    property = models.ForeignKey("properties.Property", on_delete=models.PROTECT)
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tenant_agreements",
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="landlord_agreements",
    )
    terms = models.JSONField(default=dict)
    pdf = models.FileField(upload_to="agreements/", blank=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_ACCEPTANCE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agreement #{self.id} - {self.property}"
