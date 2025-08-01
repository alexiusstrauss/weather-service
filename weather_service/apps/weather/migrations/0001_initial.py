# Generated by Django 4.2.23 on 2025-07-30 23:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WeatherCache",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("city", models.CharField(db_index=True, max_length=100, unique=True)),
                ("data", models.JSONField()),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="WeatherQuery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("city", models.CharField(db_index=True, max_length=100)),
                ("ip_address", models.GenericIPAddressField(db_index=True)),
                ("temperature", models.FloatField()),
                ("description", models.CharField(max_length=200)),
                ("humidity", models.IntegerField(blank=True, null=True)),
                ("pressure", models.FloatField(blank=True, null=True)),
                ("wind_speed", models.FloatField(blank=True, null=True)),
                ("country", models.CharField(blank=True, max_length=2, null=True)),
                ("created_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["city", "ip_address", "-created_at"], name="weather_wea_city_6d4683_idx"),
                    models.Index(fields=["-created_at"], name="weather_wea_created_730289_idx"),
                ],
            },
        ),
    ]
