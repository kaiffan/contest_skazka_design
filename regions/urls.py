from django.urls import path
from regions.views import all_regions_user_view, all_regions_contest_view

urlpatterns = [
    path(route="all/user", view=all_regions_user_view, name="all_regions_view"),
    path(
        route="all/contest",
        view=all_regions_contest_view,
        name="all_regions_contest_view",
    ),
]
