from django.conf import settings
from django.db import models


class RentalTenancy(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        NOTICE_GIVEN = "notice_given", "Notice Given"
        ENDED = "ended", "Ended"
        CANCELLED = "cancelled", "Cancelled"

    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.PROTECT,
        related_name="tenancies",
    )
    agreement = models.OneToOneField(
        "agreements.Agreement",
        on_delete=models.PROTECT,
        related_name="tenancy",
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rental_tenancies",
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="landlord_tenancies",
    )
    payment = models.OneToOneField(
        "payments.PaymentTransaction",
        on_delete=models.PROTECT,
        related_name="tenancy",
    )
    rent_amount = models.PositiveIntegerField(default=0)
    security_deposit = models.PositiveIntegerField(default=0)
    platform_fee = models.PositiveIntegerField(default=0)
    agent_commission = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.property} tenancy for {self.tenant}"
