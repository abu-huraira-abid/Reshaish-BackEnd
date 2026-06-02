from django.contrib import admin

from agreements.models import Agreement, KeyHandover


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "tenant", "landlord", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("property__title", "tenant__email", "landlord__email")


admin.site.register(KeyHandover)
