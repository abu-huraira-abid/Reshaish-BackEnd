from rest_framework.exceptions import ValidationError

from flatmates.models import FlatmateListing
from rentals.models import RentalTenancy


def create_flatmate_listing(*, user, **data):
    tenancy = data.get("tenancy")
    if not tenancy:
        raise ValidationError("Active rental is required.")
    if not isinstance(tenancy, RentalTenancy):
        tenancy = RentalTenancy.objects.filter(id=tenancy).first()
    if not tenancy or tenancy.tenant_id != user.id:
        raise ValidationError("You can only list your own rented property.")
    if tenancy.status not in [
        RentalTenancy.Status.ACTIVE,
        RentalTenancy.Status.NOTICE_GIVEN,
    ]:
        raise ValidationError("Only active rentals can be listed for flatmates.")

    listing, _ = FlatmateListing.objects.update_or_create(
        tenancy=tenancy,
        defaults={
            **data,
            "created_by": user,
            "tenancy": tenancy,
        },
    )
    return listing
