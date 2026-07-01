from django.utils import timezone
from rest_framework import serializers

from flatmates.models import FlatmateConversation, FlatmateMessage


class FlatmateMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = FlatmateMessage
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_name",
            "body",
            "is_me",
            "read_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "conversation",
            "sender",
            "sender_name",
            "is_me",
            "read_at",
            "created_at",
        ]

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.email

    def get_is_me(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.id == obj.sender_id)


class FlatmateConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    listing_detail = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = FlatmateConversation
        fields = [
            "id",
            "listing",
            "listing_detail",
            "other_user",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_other_user(self, obj):
        request = self.context.get("request")
        user = (
            obj.participants.exclude(id=request.user.id).first()
            if request and request.user.is_authenticated
            else obj.participants.first()
        )
        if not user:
            return None
        return {
            "id": user.id,
            "name": user.get_full_name() or user.email,
            "email": user.email,
            "profile_photo": user.profile_photo.url if user.profile_photo else "",
        }

    def get_listing_detail(self, obj):
        if not obj.listing_id:
            return None
        listing = obj.listing
        return {
            "id": listing.id,
            "title": listing.title,
            "property_title": listing.tenancy.property.title,
            "city": listing.tenancy.property.city,
        }

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()
        if not message:
            return None
        return {
            "id": message.id,
            "body": message.body,
            "sender": message.sender_id,
            "created_at": message.created_at,
        }

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        return obj.messages.filter(read_at__isnull=True).exclude(sender=request.user).count()


def mark_messages_read(conversation, user):
    conversation.messages.filter(read_at__isnull=True).exclude(sender=user).update(
        read_at=timezone.now()
    )
