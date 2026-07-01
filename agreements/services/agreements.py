from agreements.models import Agreement


def create_agreement(**data):
    property_obj = data.get("property")
    tenant = data.get("tenant")
    landlord = data.get("landlord")
    if property_obj and tenant and landlord:
        existing = (
            Agreement.objects.filter(
                property=property_obj,
                tenant=tenant,
                landlord=landlord,
                status__in=[
                    Agreement.Status.PENDING_ACCEPTANCE,
                    Agreement.Status.PAYMENT_PENDING,
                    Agreement.Status.ACTIVE,
                ],
            )
            .order_by("-updated_at", "-created_at", "-id")
            .first()
        )
        if existing:
            if data.get("terms") and existing.status != Agreement.Status.ACTIVE:
                existing.terms = {**(existing.terms or {}), **data["terms"]}
                existing.save(update_fields=["terms", "updated_at"])
            return existing

    return Agreement.objects.create(**data)
