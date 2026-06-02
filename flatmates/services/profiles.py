from flatmates.models import FlatmateProfile


def create_flatmate_profile(*, user, **data):
    return FlatmateProfile.objects.create(user=user, **data)
