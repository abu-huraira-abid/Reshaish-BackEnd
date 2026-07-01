from flatmates.models import FlatmateProfile


def create_flatmate_profile(*, user, **data):
    profile, _ = FlatmateProfile.objects.update_or_create(
        user=user,
        defaults=data,
    )
    return profile
