# Generated by Django 3.2.13 on 2022-08-27 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("telemetry", "0004_refactor_telemetry_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="telemetry",
            name="device_locator",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="telemetry",
            name="type",
            field=models.CharField(
                choices=[
                    ("addupi", "Adcon addUPI"),
                    ("meteoview2", "Metrica MeteoView2"),
                ],
                help_text=(
                    "The type of the system from which the data is to be fetched. If "
                    "unlisted, it might mean that it is currently unsupported."
                ),
                max_length=30,
                verbose_name="Telemetry system type",
            ),
        ),
    ]