from django.conf import settings
from django.db import models


class PaymentTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    agreement = models.ForeignKey(
        "agreements.Agreement",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount_breakdown = models.JSONField(default=dict)
    gateway_ref = models.CharField(max_length=120, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.status}"

    @property
    def total_amount(self):
        return sum(int(value or 0) for value in self.amount_breakdown.values())
