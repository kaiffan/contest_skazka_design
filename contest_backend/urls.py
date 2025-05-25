from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(route="admin/", view=admin.site.urls),
    path(route="api/v1/auth/", view=include("authentication.urls")),
    path(route="api/v1/competencies/", view=include("competencies.urls")),
    path(route="api/v1/regions/", view=include("regions.urls")),
    path(route="api/v1/users/", view=include("users.urls")),
    path(route="api/v1/applications/", view=include("applications.urls")),
    path(route="api/v1/contest_categories/", view=include("contest_categories.urls")),
    path(route="api/v1/contests/", view=include("contests.urls")),
    path(route="api/v1/criteria/", view=include("criteria.urls")),
    path(route="api/v1/nomination/", view=include("nomination.urls")),
    path(route="api/v1/contest_stage/", view=include("contest_stage.urls")),
    path(route="api/v1/age_category/", view=include("age_categories.urls")),
    path(route="api/v1/news/", view=include("vk_news.urls")),
]
