from visits.models import VisitRequest


def create_visit_request(*, tenant, **data):
    return VisitRequest.objects.create(tenant=tenant, **data)
