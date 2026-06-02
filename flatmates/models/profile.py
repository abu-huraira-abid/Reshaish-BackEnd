from django.conf import settings
from django.db import models


class FlatmateProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flatmate_profile",
    )
    city = models.CharField(max_length=100)
    budget = models.PositiveIntegerField()
    preferences = models.JSONField(default=dict, blank=True)
    match_visibility = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Flatmate profile for {self.user.email}"
