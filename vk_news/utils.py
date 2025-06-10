from datetime import datetime

from django.db import transaction
from requests import RequestException
from django.core.cache import cache
from django.utils.timezone import make_aware
from config.settings import get_settings
from vk_news.models import VkNews
from vk_news.serializers import VkNewsSerializer
from vk_news_attachments.models import VkNewsAttachment
import requests


def clean_text(text: str) -> str:
    """Удаляет лишние пробелы и перевод строки."""
    return " ".join(text.strip().replace("\n", " ").split())


def format_date(timestamp: int) -> datetime:
    return make_aware(datetime.fromtimestamp(timestamp))


def extract_photo(photo_data: dict):
    return photo_data.get("orig_photo") or max(
        photo_data.get("sizes", []),
        key=lambda size: size.get("width", 0) * size.get("height", 0),
        default=None,
    )


def get_posts_with_api(
        token: str,
        domain: str,
        count: int,
        version: str = "5.199",
):
    params = {
        "domain": domain,
        "access_token": token,
        "v": version,
        "count": count,
    }

    response = requests.get(url="https://api.vk.com/method/wall.get", params=params)
    response.raise_for_status()
    return response.json()


def save_vk_post_to_database(items: dict):
    post_id = items.get("id")
    text = clean_text(items.get("text", ""))
    date = format_date(items.get("date", 0))

    with transaction.atomic():
        if VkNews.objects.filter(vk_id=post_id).exists():
            return False

        photo_data = None
        for attachment in items.get("attachments", []):
            if attachment.get("type") == "photo":
                photo_data = extract_photo(attachment.get("photo", {}))
                break

        attachment_obj = None
        if photo_data:
            attachment_obj, _ = VkNewsAttachment.objects.get_or_create(
                url=photo_data.get("url"),
                defaults={
                    "width": photo_data.get("width"),
                    "height": photo_data.get("height"),
                    "type": "photo",
                },
            )

        VkNews.objects.create(
            vk_id=post_id,
            description=text,
            date=date,
            vk_attachment=attachment_obj,
            url=f"https://vk.com/wall{items.get('owner_id', '')}_{post_id}",
        )
    return True


def fetch_vk_posts_with_api() -> dict[str, str]:
    settings = get_settings()

    try:
        data = get_posts_with_api(
            token=settings.vk_credentials.TOKEN,
            domain=settings.vk_credentials.DOMAIN,
            count=settings.vk_credentials.COUNT_POSTS,
            version=settings.vk_credentials.API_VERSION,
        )
    except RequestException as e:
        return {"error": f"Ошибка при запросе к VK API: {str(e)}"}

    items = data.get("response", {}).get("items", [])

    if not items:
        return {"info": "Нет новых постов в ответе от VK."}

    saved_count = 0
    for item in items:
        if save_vk_post_to_database(item):
            saved_count += 1

    return {"saved": str(saved_count), "total": str(len(items))}


def get_news_response():
    cached = cache.get(key="latest_vk_news")
    if not cached:
        recent_news = VkNews.objects.select_related("vk_attachment").order_by(
            "-created_at"
        )[:5]
        serialized_news = VkNewsSerializer(recent_news, many=True).data
        cache.set(key="latest_vk_news", value=serialized_news, timeout=3600)
        return serialized_news
    return cached
