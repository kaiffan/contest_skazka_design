from datetime import timedelta

from django.utils import timezone
from requests import RequestException
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from django.core.cache import cache

from vk_news.models import VkNews
from vk_news import utils


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_vk_news_view(request: Request) -> Response:
    threshold = timezone.now() - timedelta(hours=24)

    if VkNews.objects.filter(created_at__gt=threshold).exists():
        news_data = utils.get_news_response()
        return Response(
            data={
                "message": "Меньше 24 часов с последнего обновления. Возвращаю последние 5 новостей.",
                "news": news_data,
            },
            status=status.HTTP_200_OK,
        )

    try:
        cache.delete(key="latest_vk_news")
        saved_news_count = utils.fetch_vk_posts_with_api()
        news_data = utils.get_news_response()
        return Response(
            data={
                "message": f"Добавлено новых новостей: {saved_news_count}",
                "news": news_data,
            },
            status=status.HTTP_201_CREATED,
        )
    except RequestException as exception:
        print(f"[VK API] Ошибка при запросе к ВКонтакте: {exception}")
        news_data = utils.get_news_response()
        return Response(
            data={"error": "Не удалось обновить новости из ВК", "news": news_data},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
