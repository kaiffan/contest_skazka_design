# Generated by Django 5.2 on 2025-05-25 14:46

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("applications", "0001_initial"),
        ("criteria", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkRate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rate",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ]
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="applications.applications",
                    ),
                ),
                (
                    "criteria",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="criteria.criteria",
                    ),
                ),
            ],
            options={
                "db_table": "work_rate",
                "unique_together": {("criteria", "application")},
            },
        ),
    ]
