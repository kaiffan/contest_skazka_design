from django.urls import path

from vk_news.views import get_vk_news_view

urlpatterns = [
    path(
        route="latest",
        view=get_vk_news_view,
        name="get_vk_news_view",
    )
]
