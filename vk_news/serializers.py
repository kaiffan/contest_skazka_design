from rest_framework.serializers import ModelSerializer

from vk_news.models import VkNews
from vk_news_attachments.serializers import VkNewsAttachmentSerializer


class VkNewsSerializer(ModelSerializer[VkNews]):
    vk_attachment = VkNewsAttachmentSerializer()

    class Meta:
        model = VkNews
        fields = ["vk_id", "description", "date", "url", "vk_attachment"]
