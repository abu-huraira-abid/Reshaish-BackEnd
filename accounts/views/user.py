from django.contrib.auth import get_user_model
from rest_framework import decorators, permissions, response, status, viewsets

from accounts.permissions import IsAdminOrReadSelf
from accounts.serializers import ChangePasswordSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadSelf]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return User.objects.all().order_by("-date_joined")
        return User.objects.filter(id=self.request.user.id)

    @decorators.action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )

    @decorators.action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        if request.user.role != User.Role.ADMIN:
            return response.Response(
                {"detail": "Only admins can suspend accounts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()
        if user == request.user:
            return response.Response(
                {"detail": "You cannot suspend your own admin account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])
        return response.Response(self.get_serializer(user).data)

    @decorators.action(detail=True, methods=["post"], url_path="reactivate")
    def reactivate(self, request, pk=None):
        if request.user.role != User.Role.ADMIN:
            return response.Response(
                {"detail": "Only admins can reactivate accounts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        return response.Response(self.get_serializer(user).data)
