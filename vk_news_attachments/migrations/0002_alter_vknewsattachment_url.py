# Generated by Django 5.2.2 on 2025-06-10 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vk_news_attachments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vknewsattachment",
            name="url",
            field=models.URLField(
                db_index=True, max_length=1024, verbose_name="URL изображения"
            ),
        ),
    ]
