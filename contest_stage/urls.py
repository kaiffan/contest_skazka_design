from django.urls import path

from contest_stage.views import all_contest_stage_view

urlpatterns = [
    path(route="all", view=all_contest_stage_view, name="all_contest_stage_view")
]
