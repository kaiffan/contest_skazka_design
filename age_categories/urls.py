from django.urls import path

from age_categories.views import get_age_categories_view

urlpatterns = [
    path(route="all", view=get_age_categories_view, name="get_age_categories_view")
]
