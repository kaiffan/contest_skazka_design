from django.db import models


class VkNews(models.Model):
    vk_id = models.BigIntegerField(unique=True)
    description = models.TextField()
    date = models.DateTimeField(blank=False, null=False)
    vk_attachment = models.ForeignKey(
        to="vk_news_attachments.VkNewsAttachment", on_delete=models.CASCADE
    )
    url = models.URLField(null=True, blank=True, max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vk_news"
