from django.urls import path
from contests.views import (
    create_contest_view,
    publish_contest_view,
    update_contest_view,
    delete_contest_view,
)

urlpatterns = [
    path(route="", view=create_contest_view, name="create_contest_view"),
    path(route="", view=update_contest_view, name="update_contest_view"),
    path(route="admin/publish", view=publish_contest_view, name="publish_contest_view"),
    path(route="", view=delete_contest_view, name="delete_contest_view"),
]
