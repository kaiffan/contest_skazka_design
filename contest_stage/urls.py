from django.urls import path

from contest_stage.views import (
    all_contest_stage_view,
    add_or_remove_contest_stage_in_contest_view,
)

urlpatterns = [
    path(route="all", view=all_contest_stage_view, name="all_contest_stage_view"),
    path(
        route="change",
        view=add_or_remove_contest_stage_in_contest_view,
        name="add_or_remove_contest_stage_in_contest_view",
    ),
]
