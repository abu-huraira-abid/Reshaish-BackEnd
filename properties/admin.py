from django.contrib import admin

from properties.models import Property, VerificationReport


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "city", "rent", "status", "created_at")
    list_filter = ("status", "property_type", "city")
    search_fields = ("title", "address", "city", "owner__email")


@admin.register(VerificationReport)
class VerificationReportAdmin(admin.ModelAdmin):
    list_display = ("property", "agent", "decision", "created_at")
    list_filter = ("decision", "created_at")
    search_fields = ("property__title", "agent__email")
