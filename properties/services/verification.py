from properties.models import Property, VerificationReport


def create_verification_report(*, agent, **data):
    report = VerificationReport.objects.create(agent=agent, **data)
    new_status = {
        VerificationReport.Decision.VERIFIED: Property.Status.VERIFIED,
        VerificationReport.Decision.REJECTED: Property.Status.REJECTED,
        VerificationReport.Decision.NEED_EVIDENCE: Property.Status.PENDING,
    }[report.decision]
    Property.objects.filter(id=report.property_id).update(status=new_status)
    return report
