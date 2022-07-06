# Generated by Django 3.2.13 on 2022-07-04 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discount", "0042_migrate_orderdiscount_id_to_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="sale",
            name="ended_notification_sent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sale",
            name="started_notification_sent",
            field=models.BooleanField(default=False),
        ),
    ]