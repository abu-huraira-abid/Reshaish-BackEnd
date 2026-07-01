from datetime import timedelta
from email.mime.image import MIMEImage

import pyotp
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import EmailOTP


def create_email_otp(user):
    expiry_minutes = getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10)
    interval = 60 * expiry_minutes
    otp_secret = pyotp.random_base32()
    code = pyotp.TOTP(otp_secret, digits=6, interval=interval).now()
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
    EmailOTP.objects.filter(
        user=user,
        purpose=EmailOTP.Purpose.VERIFY_EMAIL,
        consumed_at__isnull=True,
    ).update(consumed_at=timezone.now())
    EmailOTP.create_for_user(user, otp_secret=otp_secret, expires_at=expires_at)
    return code, expires_at


def send_email_verification_otp(user):
    code, expires_at = create_email_otp(user)
    context = {
        "code": code,
        "expires_at": expires_at,
        "expiry_minutes": getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10),
        "user": user,
        "app_name": "Rehaish",
        "support_email": getattr(settings, "DEFAULT_FROM_EMAIL", "support@rehaish.com"),
    }
    subject = "Verify your Rehaish email"
    html_body = render_to_string("accounts/email/verify_email_otp.html", context)
    text_body = (
        f"Your Rehaish verification code is {code}. "
        f"It expires in {context['expiry_minutes']} minutes."
    )
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    logo_path = settings.BASE_DIR / "accounts/static/accounts/img/rehaish-logo.png"
    if logo_path.exists():
        with logo_path.open("rb") as logo_file:
            logo = MIMEImage(logo_file.read())
        logo.add_header("Content-ID", "<rehaish-logo>")
        logo.add_header("Content-Disposition", "inline", filename="rehaish-logo.png")
        message.attach(logo)
    message.send(fail_silently=False)
    return expires_at
