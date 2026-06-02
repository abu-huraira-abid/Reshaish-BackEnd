from django.db import models


class VisitCheckIn(models.Model):
    visit = models.OneToOneField(
        "visits.VisitRequest",
        on_delete=models.CASCADE,
        related_name="checkin",
    )
    tenant_scan_time = models.DateTimeField(null=True, blank=True)
    agent_scan_time = models.DateTimeField(null=True, blank=True)
    checkout_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Check-in for visit {self.visit_id}"
