from properties.models import Property


def create_property(*, owner, **data):
    return Property.objects.create(owner=owner, status=Property.Status.PENDING, **data)
