from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def _attach_logo(message):
    logo_path = settings.BASE_DIR / "accounts/static/accounts/img/rehaish-logo.png"
    if not logo_path.exists():
        return

    with logo_path.open("rb") as logo_file:
        logo = MIMEImage(logo_file.read())
    logo.add_header("Content-ID", "<rehaish-logo>")
    logo.add_header("Content-Disposition", "inline", filename="rehaish-logo.png")
    message.attach(logo)


def _send_onboarding_review_email(onboarding, *, subject, headline, intro, reason=""):
    user = onboarding.user
    context = {
        "app_name": "Rehaish",
        "headline": headline,
        "intro": intro,
        "onboarding": onboarding,
        "reason": reason,
        "status_label": onboarding.get_status_display(),
        "support_email": getattr(settings, "DEFAULT_FROM_EMAIL", "support@rehaish.com"),
        "user": user,
    }
    html_body = render_to_string("accounts/email/onboarding_review.html", context)
    text_body = intro
    if reason:
        text_body = f"{intro}\n\nReason: {reason}"

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    _attach_logo(message)
    message.send(fail_silently=False)


def send_onboarding_approved_email(onboarding):
    _send_onboarding_review_email(
        onboarding,
        subject="Your Rehaish account has been approved",
        headline="Your account is approved",
        intro=(
            "Good news. Your Rehaish identity verification has been approved, "
            "and your account is ready to use."
        ),
    )


def send_onboarding_rejected_email(onboarding):
    reason = onboarding.rejection_reason.strip()
    _send_onboarding_review_email(
        onboarding,
        subject="Your Rehaish verification needs an update",
        headline="Verification needs an update",
        intro=(
            "Your Rehaish identity verification could not be approved yet. "
            "Please review the reason below and submit your onboarding again."
        ),
        reason=reason,
    )
