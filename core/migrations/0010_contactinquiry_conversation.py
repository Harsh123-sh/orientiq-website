from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_contactinquiry_consented_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactinquiry",
            name="conversation_reference",
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="contactinquiry",
            name="conversation_transcript",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
