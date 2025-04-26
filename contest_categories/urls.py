from django.urls import path

from contest_categories.views import all_contest_categories_view

urlpatterns = [
    path(
        route="", view=all_contest_categories_view, name="all_contest_categories_view"
    ),
]
