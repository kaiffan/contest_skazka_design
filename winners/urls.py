from django.urls import path

from winners.views import get_contest_winners_view

urlpatterns = [
    path(route="all", view=get_contest_winners_view, name="get_contest_winners_view"),
]
