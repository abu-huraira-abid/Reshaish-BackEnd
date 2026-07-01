from django.db.models import Count
from rest_framework.exceptions import ValidationError

from accounts.models import User
from flatmates.models import FlatmateConversation, FlatmateListing, FlatmateMessage


def get_or_create_conversation(*, user, recipient_id, listing_id=None):
    if not recipient_id:
        raise ValidationError("Recipient is required.")
    if user.id == int(recipient_id):
        raise ValidationError("You cannot start a conversation with yourself.")

    recipient = User.objects.filter(id=recipient_id, role=User.Role.TENANT).first()
    if not recipient:
        raise ValidationError("Flatmate recipient was not found.")

    listing = None
    if listing_id:
        listing = FlatmateListing.objects.filter(id=listing_id).first()
        if not listing:
            raise ValidationError("Flatmate listing was not found.")

    conversation = (
        FlatmateConversation.objects.annotate(participant_count=Count("participants"))
        .filter(participants=user)
        .filter(participants=recipient)
        .filter(participant_count=2)
        .first()
    )
    if not conversation:
        conversation = FlatmateConversation.objects.create(listing=listing)
        conversation.participants.add(user, recipient)
    return conversation


def send_message(*, conversation, sender, body):
    if not conversation.participants.filter(id=sender.id).exists():
        raise ValidationError("You are not a participant in this conversation.")
    body = str(body or "").strip()
    if not body:
        raise ValidationError("Message cannot be empty.")
    message = FlatmateMessage.objects.create(
        conversation=conversation,
        sender=sender,
        body=body,
    )
    conversation.save(update_fields=["updated_at"])
    return message
