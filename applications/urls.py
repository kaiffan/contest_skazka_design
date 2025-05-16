from django.urls import path

from applications.views import (
    send_applications_view,
    approve_application_view,
    reject_application_view,
    get_all_applications_view,
    get_application_view,
    get_all_applications_approved_view,
    get_all_applications_rejected_view,
)
from work_rate.views import (
    work_rate_view,
    get_all_rated_works_in_contest_view,
    update_rated_work_view,
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
        route="all/rejected",
        view=get_all_applications_rejected_view,
        name="get_all_applications_rejected_view",
    ),
    path(route="", view=get_application_view, name="get_application_view"),
    path(route="rate", view=work_rate_view, name="work_rate_view"),
    path(
        route="rate/update", view=update_rated_work_view, name="update_rated_work_view"
    ),
    path(
        route="all/rate",
        view=get_all_rated_works_in_contest_view,
        name="get_all_rated_works_view",
    ),
]
