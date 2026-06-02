from django.contrib import admin

from payments.models import CommissionLedger, PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "agreement", "payer", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("payer__email", "gateway_ref")


admin.site.register(CommissionLedger)
