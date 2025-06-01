from .views import upload_file_view
from django.urls import path

urlpatterns = [
    path(route="upload", view=upload_file_view, name="upload_file_view"),
]
