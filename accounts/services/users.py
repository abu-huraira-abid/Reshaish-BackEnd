from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(*, password, **user_data):
    user = User(**user_data)
    user.set_password(password)
    user.save()
    return user
