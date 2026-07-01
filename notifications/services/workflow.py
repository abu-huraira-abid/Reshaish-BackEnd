from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from audit.services import record_audit_log
from notifications.models import Notification

User = get_user_model()


def _frontend_url(path):
    base_url = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _qr_image_url(token_value):
    data = _frontend_url(f"/agent/qr-support?token={token_value}")
    return (
        "https://api.qrserver.com/v1/create-qr-code/"
        f"?size=220x220&data={data}"
    )


def _attach_logo(message):
    logo_path = settings.BASE_DIR / "accounts/static/accounts/img/rehaish-logo.png"
    if not logo_path.exists():
        return

    with logo_path.open("rb") as logo_file:
        logo = MIMEImage(logo_file.read())
    logo.add_header("Content-ID", "<rehaish-logo>")
    logo.add_header("Content-Disposition", "inline", filename="rehaish-logo.png")
    message.attach(logo)


def _send_workflow_email(
    *,
    subject,
    recipients,
    recipient=None,
    eyebrow="Property verification",
    headline,
    intro,
    body,
    property_title,
    city="",
    scheduled_at="",
    status_label="",
    qr_url="",
    qr_code="",
    cta_label="",
    cta_path="",
):
    recipients = [email for email in recipients if email]
    if not recipients:
        return

    cta_url = _frontend_url(cta_path) if cta_path else ""
    context = {
        "body": body,
        "city": city,
        "cta_label": cta_label,
        "cta_url": cta_url,
        "eyebrow": eyebrow,
        "headline": headline,
        "intro": intro,
        "property_title": property_title,
        "qr_code": qr_code,
        "qr_url": qr_url,
        "recipient": recipient,
        "scheduled_at": scheduled_at,
        "status_label": status_label,
    }
    html_body = render_to_string("notifications/email/workflow_event.html", context)
    text_body = "\n\n".join(
        part
        for part in [
            headline,
            intro,
            f"Property: {property_title}",
            f"City: {city}" if city else "",
            f"Visit time: {scheduled_at}" if scheduled_at else "",
            f"Status: {status_label}" if status_label else "",
            f"QR token: {qr_code}" if qr_code else "",
            body,
            cta_url,
        ]
        if part
    )
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    message.attach_alternative(html_body, "text/html")
    _attach_logo(message)
    message.send(fail_silently=False)


def notify_user(
    *,
    recipient,
    event_type,
    title,
    message,
    actor=None,
    url="",
    metadata=None,
):
    if not recipient:
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        event_type=event_type,
        title=title,
        message=message,
        url=url,
        metadata=metadata or {},
    )


def notify_admins(*, event_type, title, message, actor=None, url="", metadata=None):
    notifications = [
        Notification(
            recipient=admin,
            actor=actor,
            event_type=event_type,
            title=title,
            message=message,
            url=url,
            metadata=metadata or {},
        )
        for admin in User.objects.filter(role=User.Role.ADMIN, is_active=True)
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)


def send_onboarding_submitted_notification(onboarding):
    user = onboarding.user
    title = "New onboarding request"
    message = (
        f"{user.email} submitted {user.get_role_display()} onboarding for admin "
        "approval."
    )
    notify_admins(
        actor=user,
        event_type=Notification.EventType.ONBOARDING_SUBMITTED,
        title=title,
        message=message,
        url="/admin/onboarding",
        metadata={"onboarding_id": onboarding.id, "user_id": user.id},
    )
    record_audit_log(
        actor=user,
        action="onboarding_submitted",
        entity_type="user_onboarding",
        entity_id=str(onboarding.id),
        metadata={"role": user.role, "status": onboarding.status},
    )


def send_property_listed_notifications(property_obj):
    agents = User.objects.filter(
        role=User.Role.AGENT,
        city__iexact=property_obj.city,
        is_active=True,
    )
    notified_agents = list(agents)
    title = "New property needs verification"
    message = (
        f"{property_obj.title} in {property_obj.city} was submitted by "
        f"{property_obj.owner.email}. Please schedule a verification visit."
    )
    url = "/agent/verifications"
    for agent in notified_agents:
        notify_user(
            recipient=agent,
            actor=property_obj.owner,
            event_type=Notification.EventType.PROPERTY_LISTED,
            title=title,
            message=message,
            url=url,
            metadata={"property_id": property_obj.id},
        )

    for agent in notified_agents:
        _send_workflow_email(
            subject="New Rehaish property needs verification",
            recipients=[agent.email],
            recipient=agent,
            eyebrow="Agent assignment",
            headline="New property needs verification",
            intro=(
                "a new property in your city has been submitted and needs a "
                "verification visit scheduled."
            ),
            body=message,
            property_title=property_obj.title,
            city=property_obj.city,
            status_label=property_obj.get_status_display(),
            cta_label="Open verifications",
            cta_path="/agent/verifications",
        )
    _send_workflow_email(
        subject="New Rehaish property needs verification",
        recipients=[
            admin.email
            for admin in User.objects.filter(role=User.Role.ADMIN, is_active=True)
        ],
        eyebrow="Admin activity",
        headline="Property listed for verification",
        intro="a landlord submitted a property and same-city agents were notified.",
        body=message,
        property_title=property_obj.title,
        city=property_obj.city,
        status_label=property_obj.get_status_display(),
        cta_label="Open listing moderation",
        cta_path="/admin/moderation",
    )
    notify_admins(
        actor=property_obj.owner,
        event_type=Notification.EventType.PROPERTY_LISTED,
        title="Property listed for verification",
        message=message,
        url="/admin/moderation",
        metadata={"property_id": property_obj.id},
    )
    record_audit_log(
        actor=property_obj.owner,
        action="property_listed",
        entity_type="property",
        entity_id=str(property_obj.id),
        metadata={"city": property_obj.city, "agent_count": agents.count()},
    )


def send_verification_visit_scheduled_notifications(visit, qr_token):
    property_obj = visit.property
    scheduled_at = timezone.localtime(visit.confirmed_slot).strftime(
        "%d %b %Y, %I:%M %p"
    )
    title = "Verification visit scheduled"
    message = (
        f"{visit.agent.email} scheduled verification for {property_obj.title} "
        f"on {scheduled_at}."
    )
    notify_user(
        recipient=property_obj.owner,
        actor=visit.agent,
        event_type=Notification.EventType.VERIFICATION_VISIT_SCHEDULED,
        title=title,
        message=f"{message} QR code: {qr_token.token_value}",
        url="/landlord/listings",
        metadata={
            "property_id": property_obj.id,
            "visit_id": visit.id,
            "qr_token": qr_token.token_value,
        },
    )
    _send_workflow_email(
        subject="Rehaish property verification visit scheduled",
        recipients=[property_obj.owner.email],
        recipient=property_obj.owner,
        eyebrow="Verification visit",
        headline="Your verification visit is scheduled",
        intro=(
            "your assigned Rehaish agent has scheduled a property "
            "verification visit."
        ),
        body=(
            "Please keep this QR code ready. The agent must scan it at the "
            "property before the verification form can be completed."
        ),
        property_title=property_obj.title,
        city=property_obj.city,
        scheduled_at=scheduled_at,
        status_label=visit.get_status_display(),
        qr_code=qr_token.token_value,
        cta_label="View property",
        cta_path="/landlord/listings",
    )
    notify_admins(
        actor=visit.agent,
        event_type=Notification.EventType.VERIFICATION_VISIT_SCHEDULED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={"property_id": property_obj.id, "visit_id": visit.id},
    )
    record_audit_log(
        actor=visit.agent,
        action="verification_visit_scheduled",
        entity_type="visit_request",
        entity_id=str(visit.id),
        metadata={"property_id": property_obj.id, "scheduled_at": scheduled_at},
    )


def send_verification_visit_confirmed_notifications(visit, actor):
    property_obj = visit.property
    title = "Verification visit confirmed"
    message = (
        f"{actor.email} confirmed arrival for {property_obj.title}. "
        "The property verification visit is now checked in."
    )
    notify_user(
        recipient=property_obj.owner,
        actor=actor,
        event_type=Notification.EventType.VERIFICATION_VISIT_CONFIRMED,
        title=title,
        message=message,
        url="/landlord/listings",
        metadata={"property_id": property_obj.id, "visit_id": visit.id},
    )
    notify_admins(
        actor=actor,
        event_type=Notification.EventType.VERIFICATION_VISIT_CONFIRMED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={"property_id": property_obj.id, "visit_id": visit.id},
    )
    record_audit_log(
        actor=actor,
        action="verification_visit_confirmed",
        entity_type="visit_request",
        entity_id=str(visit.id),
        metadata={"property_id": property_obj.id},
    )


def send_property_status_notifications(property_obj, actor, old_status, new_status):
    title = "Property verification status updated"
    message = (
        f"{property_obj.title} changed from {old_status} to {new_status}. "
        + (
            "It is now visible to tenants."
            if new_status == "verified"
            else "Please review the latest verification result."
        )
    )
    notify_user(
        recipient=property_obj.owner,
        actor=actor,
        event_type=Notification.EventType.PROPERTY_STATUS_CHANGED,
        title=title,
        message=message,
        url="/landlord/listings",
        metadata={
            "property_id": property_obj.id,
            "old_status": old_status,
            "new_status": new_status,
        },
    )
    _send_workflow_email(
        subject="Rehaish property status updated",
        recipients=[property_obj.owner.email],
        recipient=property_obj.owner,
        eyebrow="Property status",
        headline="Your property status changed",
        intro="your property verification status has been updated.",
        body=message,
        property_title=property_obj.title,
        city=property_obj.city,
        status_label=property_obj.get_status_display(),
        cta_label="View my properties",
        cta_path="/landlord/listings",
    )
    notify_admins(
        actor=actor,
        event_type=Notification.EventType.PROPERTY_STATUS_CHANGED,
        title=title,
        message=message,
        url="/admin/moderation",
        metadata={
            "property_id": property_obj.id,
            "old_status": old_status,
            "new_status": new_status,
        },
    )
    record_audit_log(
        actor=actor,
        action="property_status_changed",
        entity_type="property",
        entity_id=str(property_obj.id),
        metadata={"old_status": old_status, "new_status": new_status},
    )


def send_tenant_visit_requested_notifications(visit):
    property_obj = visit.property
    tenant = visit.tenant
    agents = User.objects.filter(
        role=User.Role.AGENT,
        city__iexact=property_obj.city,
        is_active=True,
    )
    notified_agents = [visit.agent] if visit.agent_id else list(agents)
    title = "Tenant visit requested"
    message = (
        f"{tenant.email} requested a visit for {property_obj.title} in "
        f"{property_obj.city}. Please coordinate the meeting schedule."
    )
    for agent in notified_agents:
        notify_user(
            recipient=agent,
            actor=tenant,
            event_type=Notification.EventType.TENANT_VISIT_REQUESTED,
            title=title,
            message=message,
            url="/agent/schedule",
            metadata={"property_id": property_obj.id, "visit_id": visit.id},
        )
        _send_workflow_email(
            subject="New Rehaish tenant visit request",
            recipients=[agent.email],
            recipient=agent,
            eyebrow="Tenant visit",
            headline="A tenant requested a property visit",
            intro="a tenant wants to visit a property in your city.",
            body=message,
            property_title=property_obj.title,
            city=property_obj.city,
            status_label=visit.get_status_display(),
            cta_label="Open schedule",
            cta_path="/agent/schedule",
        )
    notify_admins(
        actor=tenant,
        event_type=Notification.EventType.TENANT_VISIT_REQUESTED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={"property_id": property_obj.id, "visit_id": visit.id},
    )
    record_audit_log(
        actor=tenant,
        action="tenant_visit_requested",
        entity_type="visit_request",
        entity_id=str(visit.id),
        metadata={
            "property_id": property_obj.id,
            "city": property_obj.city,
            "agent_count": len(notified_agents),
        },
    )


def send_tenant_visit_scheduled_notifications(visit, qr_token):
    property_obj = visit.property
    tenant = visit.tenant
    agent = visit.agent
    scheduled_at = (
        timezone.localtime(visit.confirmed_slot).strftime("%d %b %Y, %I:%M %p")
        if visit.confirmed_slot
        else "the selected slot"
    )
    title = "Tenant visit scheduled"
    message = (
        f"{property_obj.title} visit with {tenant.email} is scheduled for "
        f"{scheduled_at}."
    )
    notify_user(
        recipient=tenant,
        actor=agent,
        event_type=Notification.EventType.TENANT_VISIT_SCHEDULED,
        title=title,
        message=(
            f"{message} Keep your QR code ready for the agent. "
            f"QR code: {qr_token.token_value}"
        ),
        url="/tenant/qr",
        metadata={
            "property_id": property_obj.id,
            "visit_id": visit.id,
            "qr_token": qr_token.token_value,
        },
    )
    _send_workflow_email(
        subject="Your Rehaish property visit is scheduled",
        recipients=[tenant.email],
        recipient=tenant,
        eyebrow="Property visit",
        headline="Your property visit is scheduled",
        intro="your visit request has been scheduled.",
        body=(
            "Open your Rehaish app and show this QR code to the assigned agent "
            "when you meet. The agent must scan or enter it to confirm the visit."
        ),
        property_title=property_obj.title,
        city=property_obj.city,
        scheduled_at=scheduled_at,
        status_label=visit.get_status_display(),
        qr_code=qr_token.token_value,
        cta_label="Open my QR code",
        cta_path="/tenant/qr",
    )
    if agent:
        notify_user(
            recipient=agent,
            actor=tenant,
            event_type=Notification.EventType.TENANT_VISIT_SCHEDULED,
            title=title,
            message=message,
            url="/agent/schedule",
            metadata={"property_id": property_obj.id, "visit_id": visit.id},
        )
        _send_workflow_email(
            subject="Rehaish tenant visit scheduled",
            recipients=[agent.email],
            recipient=agent,
            eyebrow="Tenant visit",
            headline="A tenant visit is scheduled",
            intro="you have a tenant meeting to confirm in the Rehaish app.",
            body=(
                f"{message} Ask the tenant to show their QR code when you arrive, "
                "then scan or enter it from the QR scanner page."
            ),
            property_title=property_obj.title,
            city=property_obj.city,
            scheduled_at=scheduled_at,
            status_label=visit.get_status_display(),
            cta_label="Open QR scanner",
            cta_path="/agent/qr-support",
        )
    notify_admins(
        actor=agent or tenant,
        event_type=Notification.EventType.TENANT_VISIT_SCHEDULED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={"property_id": property_obj.id, "visit_id": visit.id},
    )
    record_audit_log(
        actor=agent or tenant,
        action="tenant_visit_scheduled",
        entity_type="visit_request",
        entity_id=str(visit.id),
        metadata={"property_id": property_obj.id, "scheduled_at": scheduled_at},
    )


def send_tenant_visit_confirmed_notifications(visit, actor):
    property_obj = visit.property
    title = "Tenant visit confirmed"
    message = (
        f"{actor.email} confirmed the tenant meeting for {property_obj.title}. "
        "The tenant visit is now checked in."
    )
    notify_user(
        recipient=visit.tenant,
        actor=actor,
        event_type=Notification.EventType.TENANT_VISIT_CONFIRMED,
        title=title,
        message=message,
        url="/tenant/visits",
        metadata={"property_id": property_obj.id, "visit_id": visit.id},
    )
    if property_obj.owner_id:
        notify_user(
            recipient=property_obj.owner,
            actor=actor,
            event_type=Notification.EventType.TENANT_VISIT_CONFIRMED,
            title=title,
            message=message,
            url="/landlord/requests",
            metadata={"property_id": property_obj.id, "visit_id": visit.id},
        )
    notify_admins(
        actor=actor,
        event_type=Notification.EventType.TENANT_VISIT_CONFIRMED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={"property_id": property_obj.id, "visit_id": visit.id},
    )
    record_audit_log(
        actor=actor,
        action="tenant_visit_confirmed",
        entity_type="visit_request",
        entity_id=str(visit.id),
        metadata={"property_id": property_obj.id},
    )
