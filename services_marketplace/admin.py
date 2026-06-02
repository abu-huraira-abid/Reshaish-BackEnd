from django.contrib import admin

from services_marketplace.models import ServiceOrder


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "service_type", "status", "schedule", "amount")
    list_filter = ("service_type", "status")
    search_fields = ("tenant__email", "vendor_name")
