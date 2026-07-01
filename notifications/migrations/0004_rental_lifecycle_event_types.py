from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0003_alter_notification_event_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("onboarding_submitted", "Onboarding Submitted"),
                    ("property_listed", "Property Listed"),
                    (
                        "verification_visit_scheduled",
                        "Verification Visit Scheduled",
                    ),
                    (
                        "verification_visit_confirmed",
                        "Verification Visit Confirmed",
                    ),
                    ("property_status_changed", "Property Status Changed"),
                    ("tenant_visit_requested", "Tenant Visit Requested"),
                    ("tenant_visit_scheduled", "Tenant Visit Scheduled"),
                    ("tenant_visit_confirmed", "Tenant Visit Confirmed"),
                    ("rental_payment_completed", "Rental Payment Completed"),
                    ("agent_commission_ready", "Agent Commission Ready"),
                    ("property_issue_reported", "Property Issue Reported"),
                    ("leave_notice_submitted", "Leave Notice Submitted"),
                ],
                max_length=80,
            ),
        ),
    ]
