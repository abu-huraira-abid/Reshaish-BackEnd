import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("agreements", "0001_initial"),
        ("payments", "0002_stripe_checkout_fields"),
        ("properties", "0003_propertyimage"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RentalTenancy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rent_amount", models.PositiveIntegerField(default=0)),
                ("security_deposit", models.PositiveIntegerField(default=0)),
                ("platform_fee", models.PositiveIntegerField(default=0)),
                ("agent_commission", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("notice_given", "Notice Given"),
                            ("ended", "Ended"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="active",
                        max_length=30,
                    ),
                ),
                ("start_date", models.DateField(auto_now_add=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "agreement",
                    models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="tenancy", to="agreements.agreement"),
                ),
                (
                    "landlord",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="landlord_tenancies", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "payment",
                    models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="tenancy", to="payments.paymenttransaction"),
                ),
                (
                    "property",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="tenancies", to="properties.property"),
                ),
                (
                    "tenant",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rental_tenancies", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="LeaveNotice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notice_date", models.DateField()),
                ("move_out_date", models.DateField()),
                ("reason", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("acknowledged", "Acknowledged"),
                            ("cancelled", "Cancelled"),
                            ("completed", "Completed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "submitted_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="submitted_leave_notices", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "tenancy",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="leave_notices", to="rentals.rentaltenancy"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PropertyIssue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("description", models.TextField()),
                (
                    "priority",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")],
                        default="medium",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("processing", "Processing"), ("resolved", "Resolved"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("resolution_notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "reported_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="reported_property_issues", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "tenancy",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="issues", to="rentals.rentaltenancy"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
