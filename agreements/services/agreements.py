from agreements.models import Agreement


def create_agreement(**data):
    return Agreement.objects.create(**data)
