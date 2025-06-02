from .views import upload_file_view, upload_contest_work_view
from django.urls import path

urlpatterns = [
    path(route="upload", view=upload_file_view, name="upload_file_view"),
    path(
        route="upload_contest_work",
        view=upload_contest_work_view,
        name="upload_contest_work_view",
    ),
]
