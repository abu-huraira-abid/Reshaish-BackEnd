from django.contrib import admin

from visits.models import VisitCheckIn, VisitQRToken, VisitRequest


@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ("property", "tenant", "agent", "status", "confirmed_slot")
    list_filter = ("status", "confirmed_slot")
    search_fields = ("property__title", "tenant__email", "agent__email")


admin.site.register(VisitQRToken)
admin.site.register(VisitCheckIn)
