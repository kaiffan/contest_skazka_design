# Generated by Django 5.2 on 2025-05-30 21:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("criteria", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="criteria",
            name="name",
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AddIndex(
            model_name="criteria",
            index=models.Index(fields=["name"], name="criteria_name_431550_idx"),
        ),
    ]
