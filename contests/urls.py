from django.urls import path
from contests.views import (
    create_contest_view,
    publish_contest_view,
    update_contest_view,
    delete_contest_view,
    get_all_contests_view,
    get_contest_by_id,
    get_all_contests_owner_view,
    get_all_contests_not_permissions_view, get_all_contests_jury_view,
)

urlpatterns = [
    path(route="", view=create_contest_view, name="create_contest_view"),
    path(route="update", view=update_contest_view, name="update_contest_view"),
    path(route="admin/publish", view=publish_contest_view, name="publish_contest_view"),
    path(route="admin/delete", view=delete_contest_view, name="delete_contest_view"),
    path(route="id", view=get_contest_by_id, name="get_contest_by_id_view"),
    path(route="all", view=get_all_contests_view, name="get_all_contests_view"),
    path(
        route="all/all",
        view=get_all_contests_not_permissions_view,
        name="get_all_contests_not_permissions_view",
    ),
    path(
        route="all/owner",
        view=get_all_contests_owner_view,
        name="get_all_contests_owner_view",
    ),
    path(
        route="all/jury",
        view=get_all_contests_jury_view,
        name="get_all_contests_jury_view",
    )
]
