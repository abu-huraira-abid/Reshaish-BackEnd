from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymenttransaction",
            name="currency",
            field=models.CharField(default="pkr", max_length=10),
        ),
        migrations.AddField(
            model_name="paymenttransaction",
            name="stripe_checkout_session_id",
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
        migrations.AddField(
            model_name="paymenttransaction",
            name="stripe_customer_id",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="paymenttransaction",
            name="stripe_payment_intent_id",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
