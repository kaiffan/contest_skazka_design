from django.db import models

class VkNewsAttachment(models.Model):
    url = models.URLField(verbose_name="URL изображения",
        max_length=255,
        null=False,
        blank=False,
        db_index=True
    )
    height = models.IntegerField(verbose_name="Высота изображения")
    width = models.IntegerField(verbose_name="Ширина изображения")
    type = models.CharField(
        max_length=10,
        null=False,
        blank=False
    )

    class Meta:
        db_table = "vk_news_attachments"

