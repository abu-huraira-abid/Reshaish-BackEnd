import pyotp
from django.conf import settings
from django.db import models
from django.utils import timezone


class EmailOTP(models.Model):
    class Purpose(models.TextChoices):
        VERIFY_EMAIL = "verify_email", "Verify Email"
        KEY_HANDOVER = "key_handover", "Key Handover"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_otps",
    )
    purpose = models.CharField(
        max_length=30,
        choices=Purpose.choices,
        default=Purpose.VERIFY_EMAIL,
    )
    code_hash = models.CharField(max_length=128)
    otp_secret = models.CharField(max_length=32, blank=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} OTP ({self.purpose})"

    @classmethod
    def create_for_user(
        cls,
        user,
        *,
        otp_secret,
        expires_at,
        purpose=Purpose.VERIFY_EMAIL,
    ):
        return cls.objects.create(
            user=user,
            purpose=purpose,
            code_hash="",
            otp_secret=otp_secret,
            expires_at=expires_at,
        )

    @property
    def is_consumed(self):
        return self.consumed_at is not None

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def check_code(self, code):
        self.attempts += 1
        self.save(update_fields=["attempts"])
        if not self.otp_secret:
            return False
        interval = 60 * getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10)
        totp = pyotp.TOTP(self.otp_secret, digits=6, interval=interval)
        return totp.verify(code, for_time=self.created_at, valid_window=0)

    def consume(self):
        self.consumed_at = timezone.now()
        self.save(update_fields=["consumed_at"])
