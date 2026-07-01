from django.conf import settings
from django.db import models


class LeaveNotice(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    tenancy = models.ForeignKey(
        "rentals.RentalTenancy",
        on_delete=models.CASCADE,
        related_name="leave_notices",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_leave_notices",
    )
    notice_date = models.DateField()
    move_out_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Leave notice for tenancy {self.tenancy_id}"
