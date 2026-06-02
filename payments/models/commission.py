from django.db import models


class CommissionLedger(models.Model):
    payment = models.OneToOneField(
        "payments.PaymentTransaction",
        on_delete=models.CASCADE,
        related_name="commission",
    )
    rule = models.CharField(max_length=120, default="30% of first month rent")
    commission_amount = models.PositiveIntegerField()
    settlement_amount = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commission for payment {self.payment_id}"
