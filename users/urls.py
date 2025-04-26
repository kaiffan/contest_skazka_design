from users.views import (
    contest_data_update_view,
    user_data_update_view,
    user_data_get_view, all_users_view,
)
from django.urls import path

urlpatterns = [
    path(
        route="contest_data",
        view=contest_data_update_view,
        name="contest_data_update_view",
    ),
    path(
        route="user_data",
        view=user_data_update_view,
        name="user_data_update_view",
    ),
    path(
        route="user_info",
        view=user_data_get_view,
        name="user_data_get_view",
    ),
    path(
        route="all",
        view=all_users_view,
        name="all_users_view"
    )
]
