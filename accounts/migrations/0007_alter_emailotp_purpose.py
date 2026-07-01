from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_user_profile_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailotp",
            name="purpose",
            field=models.CharField(
                choices=[
                    ("verify_email", "Verify Email"),
                    ("key_handover", "Key Handover"),
                ],
                default="verify_email",
                max_length=30,
            ),
        ),
    ]
