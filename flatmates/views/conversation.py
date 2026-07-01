from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from flatmates.models import FlatmateConversation
from flatmates.serializers import (
    FlatmateConversationSerializer,
    FlatmateMessageSerializer,
    mark_messages_read,
)
from flatmates.services import get_or_create_conversation, send_message


class FlatmateConversationViewSet(viewsets.ModelViewSet):
    serializer_class = FlatmateConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            FlatmateConversation.objects.select_related(
                "listing",
                "listing__tenancy",
                "listing__tenancy__property",
            )
            .prefetch_related("participants", "messages")
            .order_by("-updated_at", "-created_at")
        )
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(participants=user)
        return queryset.none()

    def create(self, request, *args, **kwargs):
        if request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can start flatmate conversations.")
        conversation = get_or_create_conversation(
            user=request.user,
            recipient_id=request.data.get("recipient") or request.data.get("recipient_id"),
            listing_id=request.data.get("listing") or request.data.get("listing_id"),
        )
        serializer = self.get_serializer(conversation)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.method.lower() == "post":
            message = send_message(
                conversation=conversation,
                sender=request.user,
                body=request.data.get("body") or request.data.get("text"),
            )
            serializer = FlatmateMessageSerializer(
                message,
                context=self.get_serializer_context(),
            )
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        mark_messages_read(conversation, request.user)
        serializer = FlatmateMessageSerializer(
            conversation.messages.select_related("sender"),
            many=True,
            context=self.get_serializer_context(),
        )
        return response.Response(serializer.data)
