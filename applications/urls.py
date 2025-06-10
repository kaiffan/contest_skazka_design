from django.urls import path

from applications.views import (
    send_applications_view,
    approve_application_view,
    reject_application_view,
    get_all_applications_view,
    get_application_view,
    get_all_applications_approved_view,
    get_all_applications_rejected_view,
    update_application_view,
    get_applications_user_view,
)
from work_rate.views import (
    work_rate_view,
    get_all_rated_works_in_contest_view,
    update_rated_work_view,
    get_all_rated_works_view,
    get_rated_work_by_jury_in_contest_view,
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
        route="all/contest/rate",
        view=get_all_rated_works_in_contest_view,
        name="get_all_rated_works_view",
    ),
    path(
        route="all/user",
        view=get_applications_user_view,
        name="get_applications_user_view",
    ),
    path(route="update", view=update_application_view, name="update_application_view"),
    path(
        route="all/rate", view=get_all_rated_works_view, name="get_all_rated_works_view"
    ),
    path(
        route="jury/stats",
        view=get_rated_work_by_jury_in_contest_view,
        name="get_rated_work_by_jury_in_contest_view",
    ),
]
