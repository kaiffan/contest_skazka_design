# Generated by Django 5.2.2 on 2025-06-10 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vk_news", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vknews",
            name="url",
            field=models.URLField(blank=True, max_length=1024, null=True),
        ),
    ]
