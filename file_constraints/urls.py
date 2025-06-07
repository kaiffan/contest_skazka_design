from file_constraints.views import (
    get_all_file_constraints_view,
    change_file_constraints_view,
)
from rest_framework.urls import path

urlpatterns = [
    path(
        route="all",
        view=get_all_file_constraints_view,
        name="get_all_file_constraints_view",
    ),
    path(
        route="change",
        view=change_file_constraints_view,
        name="change_file_constraints_view",
    ),
]
