from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from accounts.permissions import IsAdminOrReadSelf
from accounts.serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadSelf]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return User.objects.all().order_by("-date_joined")
        return User.objects.filter(id=self.request.user.id)
