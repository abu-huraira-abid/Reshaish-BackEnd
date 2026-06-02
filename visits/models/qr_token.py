import secrets

from django.db import models


class VisitQRToken(models.Model):
    visit = models.OneToOneField(
        "visits.VisitRequest",
        on_delete=models.CASCADE,
        related_name="qr_token",
    )
    token_value = models.CharField(
        max_length=64,
        unique=True,
        default=secrets.token_urlsafe,
    )
    expiry_time = models.DateTimeField()
    used_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR for visit {self.visit_id}"
