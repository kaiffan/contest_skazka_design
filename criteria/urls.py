from django.urls import path

from criteria.views import add_or_remove_criteria_contest_view, get_all_criteria_view

urlpatterns = [
    path(
        route="change",
        view=add_or_remove_criteria_contest_view,
        name="change_criteria_contest_view",
    ),
    path(route="", view=get_all_criteria_view, name="get_all_criteria_view"),
]
