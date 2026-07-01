from notifications.services import send_property_status_notifications
from properties.models import Property, VerificationReport


def create_verification_report(*, agent, **data):
    report = VerificationReport.objects.create(agent=agent, **data)
    property_obj = report.property
    old_status = property_obj.status
    new_status = {
        VerificationReport.Decision.VERIFIED: Property.Status.VERIFIED,
        VerificationReport.Decision.REJECTED: Property.Status.REJECTED,
        VerificationReport.Decision.NEED_EVIDENCE: Property.Status.PENDING,
    }[report.decision]
    property_obj.status = new_status
    property_obj.save(update_fields=["status", "updated_at"])
    send_property_status_notifications(property_obj, agent, old_status, new_status)
    return report
