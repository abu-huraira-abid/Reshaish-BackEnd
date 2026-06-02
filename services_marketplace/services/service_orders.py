from services_marketplace.models import ServiceOrder


def create_service_order(*, tenant, **data):
    return ServiceOrder.objects.create(tenant=tenant, **data)
