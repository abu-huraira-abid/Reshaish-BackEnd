from agreements.models import KeyHandover


def confirm_key_handover(*, confirmed_by, **data):
    return KeyHandover.objects.create(confirmed_by=confirmed_by, **data)
