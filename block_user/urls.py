from django.urls import path

from block_user.views import (
    unblock_user_view,
    block_user_view,
    get_all_blocked_users_view, get_all_users_view,
)

urlpatterns = [
    path(route="admin/block_user", view=block_user_view, name="block_user_view"),
    path(route="admin/unblock_user", view=unblock_user_view, name="unblock_user_view"),
    path(
        route="admin/all_blocked_user",
        view=get_all_blocked_users_view,
        name="get_all_blocked_users_view",
    ),
    path(
        route="admin/all_users",
        view=get_all_users_view,
        name="get_all_users_view",
    )
]
