from audit.services import record_audit_log
from notifications.models import Notification
from notifications.services import notify_admins, notify_user
from notifications.services.workflow import _send_workflow_email
from properties.models import Property
from rentals.models import RentalTenancy
from visits.models import VisitRequest


def _latest_property_agent(property_obj):
    visit = (
        VisitRequest.objects.select_related("agent")
        .filter(property=property_obj, agent__isnull=False)
        .order_by("-updated_at")
        .first()
    )
    return visit.agent if visit else None


def create_tenancy_from_payment(payment):
    agreement = payment.agreement
    property_obj = agreement.property
    breakdown = payment.amount_breakdown or {}
    rent = int(breakdown.get("rent") or property_obj.rent or 0)
    security = int(breakdown.get("deposit") or property_obj.deposit or 0)
    platform_fee = int(breakdown.get("platform_fee") or round(rent * 0.30))
    agent_commission = round(platform_fee * 0.50)

    tenancy, created = RentalTenancy.objects.get_or_create(
        agreement=agreement,
        defaults={
            "property": property_obj,
            "tenant": agreement.tenant,
            "landlord": agreement.landlord,
            "payment": payment,
            "rent_amount": rent,
            "security_deposit": security,
            "platform_fee": platform_fee,
            "agent_commission": agent_commission,
        },
    )
    property_obj.status = Property.Status.UNAVAILABLE
    property_obj.save(update_fields=["status", "updated_at"])

    agent = _latest_property_agent(property_obj)
    landlord_amount = rent + security
    title = "Property reserved after payment"
    message = (
        f"{property_obj.title} is now reserved for {agreement.tenant.email}. "
        f"Landlord payout notice: PKR {landlord_amount:,}. "
        f"Agent commission notice: PKR {agent_commission:,}."
    )
    notify_user(
        recipient=agreement.landlord,
        actor=agreement.tenant,
        event_type=Notification.EventType.RENTAL_PAYMENT_COMPLETED,
        title="Rent and security payment received",
        message=(
            f"{agreement.tenant.email} completed payment for {property_obj.title}. "
            f"Simulated transfer to landlord: PKR {landlord_amount:,}."
        ),
        url="/landlord/dashboard",
        metadata={"tenancy_id": tenancy.id, "payment_id": payment.id},
    )
    _send_workflow_email(
        subject="Rehaish payment received for your property",
        recipients=[agreement.landlord.email],
        recipient=agreement.landlord,
        eyebrow="Payment completed",
        headline="Rent and security payment received",
        intro="a tenant completed the initial payment for your property.",
        body=(
            f"Simulated transfer notice: PKR {landlord_amount:,} "
            "(rent plus security deposit)."
        ),
        property_title=property_obj.title,
        city=property_obj.city,
        status_label="Reserved",
        cta_label="Open dashboard",
        cta_path="/landlord/dashboard",
    )
    if agent:
        notify_user(
            recipient=agent,
            actor=agreement.tenant,
            event_type=Notification.EventType.AGENT_COMMISSION_READY,
            title="Agent commission ready",
            message=(
                f"Simulated agent commission for {property_obj.title}: "
                f"PKR {agent_commission:,}."
            ),
            url="/agent/dashboard",
            metadata={"tenancy_id": tenancy.id, "payment_id": payment.id},
        )
        _send_workflow_email(
            subject="Rehaish agent commission notice",
            recipients=[agent.email],
            recipient=agent,
            eyebrow="Agent commission",
            headline="Your commission is ready",
            intro="a verified property completed the initial payment flow.",
            body=f"Simulated commission notice: PKR {agent_commission:,}.",
            property_title=property_obj.title,
            city=property_obj.city,
            status_label="Commission ready",
            cta_label="Open dashboard",
            cta_path="/agent/dashboard",
        )
    notify_admins(
        actor=agreement.tenant,
        event_type=Notification.EventType.RENTAL_PAYMENT_COMPLETED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={
            "tenancy_id": tenancy.id,
            "payment_id": payment.id,
            "property_id": property_obj.id,
            "created": created,
        },
    )
    record_audit_log(
        actor=agreement.tenant,
        action="rental_payment_completed",
        entity_type="rental_tenancy",
        entity_id=str(tenancy.id),
        metadata={"property_id": property_obj.id, "payment_id": payment.id},
    )
    return tenancy


def create_issue_notifications(issue):
    tenancy = issue.tenancy
    property_obj = tenancy.property
    title = "Property issue reported"
    message = f"{issue.reported_by.email} reported {issue.title} for {property_obj.title}."
    notify_user(
        recipient=tenancy.landlord,
        actor=issue.reported_by,
        event_type=Notification.EventType.PROPERTY_ISSUE_REPORTED,
        title=title,
        message=message,
        url="/landlord/dashboard",
        metadata={"issue_id": issue.id, "tenancy_id": tenancy.id},
    )
    notify_admins(
        actor=issue.reported_by,
        event_type=Notification.EventType.PROPERTY_ISSUE_REPORTED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={"issue_id": issue.id, "tenancy_id": tenancy.id},
    )


def create_leave_notice_notifications(notice):
    tenancy = notice.tenancy
    other_party = (
        tenancy.landlord if notice.submitted_by_id == tenancy.tenant_id else tenancy.tenant
    )
    title = "Leave notice submitted"
    message = (
        f"{notice.submitted_by.email} submitted leave notice for "
        f"{tenancy.property.title}. Move-out date: {notice.move_out_date}."
    )
    tenancy.status = RentalTenancy.Status.NOTICE_GIVEN
    tenancy.save(update_fields=["status", "updated_at"])
    notify_user(
        recipient=other_party,
        actor=notice.submitted_by,
        event_type=Notification.EventType.LEAVE_NOTICE_SUBMITTED,
        title=title,
        message=message,
        url="/tenant/property-history" if other_party == tenancy.tenant else "/landlord/dashboard",
        metadata={"notice_id": notice.id, "tenancy_id": tenancy.id},
    )
    notify_admins(
        actor=notice.submitted_by,
        event_type=Notification.EventType.LEAVE_NOTICE_SUBMITTED,
        title=title,
        message=message,
        url="/admin/audit",
        metadata={"notice_id": notice.id, "tenancy_id": tenancy.id},
    )
