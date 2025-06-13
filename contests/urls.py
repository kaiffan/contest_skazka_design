from django.urls import path
from contests.views import (
    create_contest_view,
    publish_contest_view,
    update_contest_view,
    get_all_contests_view,
    get_contest_by_id_owner_view,
    get_all_contests_owner_view,
    get_all_contests_not_permissions_view,
    get_all_contests_jury_view,
    get_contest_by_id_view, get_published_contest_view, reject_publish_contest_view,
)

urlpatterns = [
    path(route="", view=create_contest_view, name="create_contest_view"),
    path(route="update", view=update_contest_view, name="update_contest_view"),
    path(route="admin/publish", view=publish_contest_view, name="publish_contest_view"),
    path(route="admin/reject", view=reject_publish_contest_view, name="reject_publish_contest_view"),
    path(route="id", view=get_contest_by_id_view, name="get_contest_by_id_view"),
    path(
        route="owner/id",
        view=get_contest_by_id_owner_view,
        name="get_contest_by_id_view",
    ),
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
    ),
    path(
        route="admin/all/published",
        view=get_published_contest_view,
        name="get_published_contest_view",
    ),
]
