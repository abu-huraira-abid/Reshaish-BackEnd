from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class User(AbstractUser):
    class Role(models.TextChoices):
        TENANT = "tenant", "Tenant"
        LANDLORD = "landlord", "Landlord"
        AGENT = "agent", "Platform Agent"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True)
    email_verified = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "role"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="unique_user_email_ci",
            ),
            models.UniqueConstraint(
                fields=["phone"],
                condition=~Q(phone=""),
                name="unique_user_phone_when_present",
            ),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.role})"
