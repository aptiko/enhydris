# Generated by Django 3.2.13 on 2022-08-14 20:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enhydris", "0111_sitesdata"),
        ("telemetry", "0002_telemetrylogmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="telemetry",
            name="password",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="telemetry",
            name="remote_station_id",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="telemetry",
            name="username",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.RenameField(
            model_name="telemetry",
            old_name="configuration",
            new_name="additional_config",
        ),
        migrations.AlterField(
            model_name="telemetry",
            name="additional_config",
            field=models.JSONField(default=dict),
        ),
        migrations.CreateModel(
            name="Sensor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sensor_id", models.CharField(max_length=20)),
                (
                    "telemetry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="telemetry.telemetry",
                    ),
                ),
                (
                    "timeseries_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="enhydris.timeseriesgroup",
                    ),
                ),
            ],
            options={
                "unique_together": {
                    ("telemetry", "sensor_id"),
                    ("telemetry", "timeseries_group"),
                },
            },
        ),
    ]
