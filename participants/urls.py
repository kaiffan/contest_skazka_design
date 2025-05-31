from django.urls import path

from participants.views import change_jury_view, change_or_committee_view

urlpatterns = [
    path(route="change_jury", view=change_jury_view, name="change_jury_view"),
    path(
        route="change_org_committe",
        view=change_or_committee_view,
        name="change_or_committee_view",
    ),
]
