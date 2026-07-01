from notifications.services import send_property_listed_notifications
from properties.models import Property


def create_property(*, owner, **data):
    property_obj = Property.objects.create(
        owner=owner,
        status=Property.Status.PENDING,
        **data,
    )
    send_property_listed_notifications(property_obj)
    return property_obj
