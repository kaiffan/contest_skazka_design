from rest_framework.serializers import ModelSerializer

from vk_news_attachments.models import VkNewsAttachment


class VkNewsAttachmentSerializer(ModelSerializer[VkNewsAttachment]):
    class Meta:
        model = VkNewsAttachment
        fields = ["url", "height", "width", "type"]
