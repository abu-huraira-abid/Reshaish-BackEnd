from django.conf import settings
from django.db import models


class FlatmateConversation(models.Model):
    listing = models.ForeignKey(
        "flatmates.FlatmateListing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="flatmate_conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"Flatmate conversation #{self.id}"


class FlatmateMessage(models.Model):
    conversation = models.ForeignKey(
        FlatmateConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flatmate_messages",
    )
    body = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message #{self.id} in conversation #{self.conversation_id}"
