from accounts.models import User
from notifications.services import send_tenant_visit_requested_notifications
from visits.models import VisitRequest


def find_same_city_agent(property_obj):
    if not property_obj or not property_obj.city:
        return None
    return (
        User.objects.filter(
            role=User.Role.AGENT,
            city__iexact=property_obj.city,
            is_active=True,
        )
        .order_by("id")
        .first()
    )


def create_visit_request(*, tenant, **data):
    if not data.get("agent"):
        data["agent"] = find_same_city_agent(data.get("property"))
    visit = VisitRequest.objects.create(tenant=tenant, **data)
    send_tenant_visit_requested_notifications(visit)
    return visit
