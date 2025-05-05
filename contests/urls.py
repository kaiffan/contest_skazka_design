from django.urls import path
from contests.views import create_contest_view, update_contest_view

urlpatterns = [
    path(route="create", view=create_contest_view, name="create_contest_view"),
    path(route="update", view=update_contest_view, name="update_contest_view"),
]
