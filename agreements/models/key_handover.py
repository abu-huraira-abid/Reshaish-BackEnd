from django.conf import settings
from django.db import models


class KeyHandover(models.Model):
    class Method(models.TextChoices):
        OTP = "otp", "OTP"
        QR = "qr", "QR"

    agreement = models.OneToOneField(
        "agreements.Agreement",
        on_delete=models.CASCADE,
        related_name="key_handover",
    )
    method = models.CharField(max_length=10, choices=Method.choices)
    proof = models.FileField(upload_to="key_handovers/", blank=True)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Key handover for agreement {self.agreement_id}"
