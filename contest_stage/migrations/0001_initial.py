# Generated by Django 5.2 on 2025-05-25 14:46

from django.db import migrations, models


def add_contest_stage(apps, schema_editor):
    ContestStage = apps.get_model("contest_stage", "ContestStage")
    for stage in ["Сбор заявок", "Оценка работы", "Подведение итогов"]:
        ContestStage.objects.get_or_create(name=stage)


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContestStage",
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
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "db_table": "contest_stage",
            },
        ),
        migrations.RunPython(add_contest_stage),
    ]
