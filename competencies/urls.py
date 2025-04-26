from django.urls import path

from competencies.views import all_competencies_view

urlpatterns = [
    path(route="all", view=all_competencies_view, name="all_competencies_view"),
]
