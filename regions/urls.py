from django.urls import path
from regions.views import all_regions_view

urlpatterns = [
    path(route="all", view=all_regions_view, name="all_regions_view"),
]
