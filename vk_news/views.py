from datetime import timedelta

from drf_spectacular.utils import extend_schema, OpenApiExample, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache
from requests import RequestException
from vk_news.utils import get_news_response, fetch_vk_posts_with_api

from .models import VkNews


@extend_schema(
    summary="Получение новостей из ВКонтакте",
    description="Возвращает последние 5 новостей из кэша или обновляет их из API ВКонтакте (если прошло более 24 часов).",
    examples=[
        OpenApiExample(
            name="Новости из кэша",
            value={
                "message": "Меньше 24 часов с последнего обновления. Возвращаю последние 5 новостей.",
                "news": [
                    {
                        "id": 1,
                        "title": "Заголовок новости",
                        "description": "Текст новости...",
                        "url": "https://vk.com/wall123_456",
                        "created_at": "2025-06-10T12:00:00Z",
                    }
                ],
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            name="Новости обновлены",
            value={
                "message": "Добавлено новых новостей: 3",
                "news": [
                    {
                        "id": 2,
                        "title": "Новая новость",
                        "description": "Свежая информация...",
                        "url": "https://vk.com/wall789_012",
                        "created_at": "2025-06-12T10:00:00Z",
                    }
                ],
            },
            response_only=True,
            status_codes=["201"],
        ),
        OpenApiExample(
            name="Ошибка API ВКонтакте",
            value={
                "error": "Не удалось обновить новости из ВК",
                "news": [
                    {
                        "id": 1,
                        "title": "Старая новость",
                        "description": "Описание старой новости...",
                        "url": "https://vk.com/wall123_456",
                        "created_at": "2025-06-10T12:00:00Z",
                    }
                ],
            },
            response_only=True,
            status_codes=["503"],
        ),
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_vk_news_view(request: Request) -> Response:
    threshold = timezone.now() - timedelta(hours=24)

    if VkNews.objects.filter(created_at__gt=threshold).exists():
        news_data = get_news_response()
        return Response(
            data={
                "message": "Меньше 24 часов с последнего обновления. Возвращаю последние 5 новостей.",
                "news": news_data,
            },
            status=status.HTTP_200_OK,
        )

    try:
        cache.delete(key="latest_vk_news")
        saved_news_count = fetch_vk_posts_with_api()
        news_data = get_news_response()
        return Response(
            data={
                "message": f"Добавлено новых новостей: {saved_news_count}",
                "news": news_data,
            },
            status=status.HTTP_201_CREATED,
        )
    except RequestException as exception:
        print(f"[VK API] Ошибка при запросе к ВКонтакте: {exception}")
        news_data = get_news_response()
        return Response(
            data={"error": "Не удалось обновить новости из ВК", "news": news_data},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
