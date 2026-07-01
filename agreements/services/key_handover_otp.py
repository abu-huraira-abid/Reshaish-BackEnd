from datetime import timedelta
from email.mime.image import MIMEImage

import pyotp
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import EmailOTP
from agreements.models import Agreement, KeyHandover


def get_tenant_property_agreement(*, tenant, property_id):
    return (
        Agreement.objects.select_related("property", "tenant", "landlord")
        .filter(
            property_id=property_id,
            tenant=tenant,
            status=Agreement.Status.ACTIVE,
        )
        .order_by("-updated_at", "-created_at", "-id")
        .first()
    )


def create_key_handover_otp(agreement):
    expiry_minutes = getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10)
    interval = 60 * expiry_minutes
    otp_secret = pyotp.random_base32()
    code = pyotp.TOTP(otp_secret, digits=6, interval=interval).now()
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
    EmailOTP.objects.filter(
        user=agreement.tenant,
        purpose=EmailOTP.Purpose.KEY_HANDOVER,
        consumed_at__isnull=True,
    ).update(consumed_at=timezone.now())
    EmailOTP.create_for_user(
        agreement.tenant,
        otp_secret=otp_secret,
        expires_at=expires_at,
        purpose=EmailOTP.Purpose.KEY_HANDOVER,
    )
    return code, expires_at


def send_key_handover_otp(agreement):
    code, expires_at = create_key_handover_otp(agreement)
    context = {
        "agreement": agreement,
        "app_name": "Rehaish",
        "code": code,
        "expires_at": expires_at,
        "expiry_minutes": getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10),
        "property": agreement.property,
        "tenant": agreement.tenant,
    }
    html_body = render_to_string("agreements/email/key_handover_otp.html", context)
    text_body = (
        f"Your Rehaish key handover OTP is {code}. "
        f"It expires in {context['expiry_minutes']} minutes."
    )
    message = EmailMultiAlternatives(
        subject="Your Rehaish key handover OTP",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[agreement.tenant.email],
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


def verify_key_handover_otp(*, agreement, code, confirmed_by, notes=""):
    otp = (
        EmailOTP.objects.filter(
            user=agreement.tenant,
            purpose=EmailOTP.Purpose.KEY_HANDOVER,
            consumed_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if not otp:
        return None, "No active OTP found. Please request a new code."
    if otp.is_expired:
        return None, "OTP expired. Please request a new code."
    if otp.attempts >= 5:
        return None, "Too many invalid attempts. Please request a new code."
    if not otp.check_code(code):
        return None, "Invalid OTP code."

    otp.consume()
    handover, _ = KeyHandover.objects.get_or_create(
        agreement=agreement,
        defaults={
            "method": KeyHandover.Method.OTP,
            "confirmed_by": confirmed_by,
            "notes": notes,
        },
    )
    return handover, ""
