from django.urls import path

from applications.views import (
    send_applications_view,
    approve_application_view,
    reject_application_view,
    get_all_applications_view,
    get_application_view,
    get_all_applications_approved_view, get_all_applications_rejected_view,
)

urlpatterns = [
    path(route="send", view=send_applications_view, name="send_application_view"),
    path(
        route="approve", view=approve_application_view, name="approve_application_view"
    ),
    path(route="reject", view=reject_application_view, name="reject_application_view"),
    path(
        route="all/pending",
        view=get_all_applications_view,
        name="get_all_applications_view",
    ),
    path(
        route="all/accepted",
        view=get_all_applications_approved_view,
        name="get_all_applications_approved_view",
    ),
path(
        route="all/accepted",
        view=get_all_applications_rejected_view,
        name="get_all_applications_rejected_view",
    ),
    path(route="", view=get_application_view, name="get_application_view"),
]
