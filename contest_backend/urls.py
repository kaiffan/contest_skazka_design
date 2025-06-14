from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path(route="admin/", view=admin.site.urls),
    path(route="api/v1/auth/", view=include("authentication.urls")),
    path(route="api/v1/competencies/", view=include("competencies.urls")),
    path(route="api/v1/users/", view=include("users.urls")),
    path(route="api/v1/applications/", view=include("applications.urls")),
    path(route="api/v1/contest_categories/", view=include("contest_categories.urls")),
    path(route="api/v1/contests/", view=include("contests.urls")),
    path(route="api/v1/criteria/", view=include("criteria.urls")),
    path(route="api/v1/nomination/", view=include("nomination.urls")),
    path(route="api/v1/contest_stage/", view=include("contest_stage.urls")),
    path(route="api/v1/age_category/", view=include("age_categories.urls")),
    path(route="api/v1/news/", view=include("vk_news.urls")),
    path(route="api/v1/participants/", view=include("participants.urls")),
    path(route="api/v1/storage/", view=include("storage_s3.urls")),
    path(route="api/v1/file_constraints/", view=include("file_constraints.urls")),
    path(route="api/v1/winners/", view=include("winners.urls")),
    path(route="api/v1/admin/", view=include("block_user.urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
