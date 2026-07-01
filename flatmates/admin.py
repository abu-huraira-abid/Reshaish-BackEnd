from django.contrib import admin

from flatmates.models import (
    FlatmateConversation,
    FlatmateListing,
    FlatmateMessage,
    FlatmateProfile,
)


@admin.register(FlatmateProfile)
class FlatmateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "budget", "match_visibility")
    list_filter = ("city", "match_visibility")
    search_fields = ("user__email", "city", "bio")


@admin.register(FlatmateListing)
class FlatmateListingAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "tenancy", "expected_share", "status")
    list_filter = ("status", "tenancy__property__city")
    search_fields = ("title", "created_by__email", "tenancy__property__title")


class FlatmateMessageInline(admin.TabularInline):
    model = FlatmateMessage
    extra = 0
    readonly_fields = ("sender", "body", "created_at", "read_at")


@admin.register(FlatmateConversation)
class FlatmateConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "created_at", "updated_at")
    filter_horizontal = ("participants",)
    inlines = [FlatmateMessageInline]
