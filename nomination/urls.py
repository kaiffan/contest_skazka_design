from django.urls import path

from nomination.views import add_or_remove_nomination_contest_view

urlpatterns = [
    path(route="change", view=add_or_remove_nomination_contest_view, name="change_nomination_view"),
]