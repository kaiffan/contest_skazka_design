from django.urls import path
from authentication.views import (
    registration_view,
    login_view,
    logout_view,
    cookie_tokens_refresh_view,
    reset_password_view,
    confirm_login_view,
)

from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path(route="registration", view=registration_view, name="registration_view"),
    path(route="login", view=login_view, name="login_view"),
    path(route="logout", view=logout_view, name="logout_view"),
    path(route="verify", view=TokenVerifyView.as_view(), name="token_verify_view"),
    path(route="refresh", view=cookie_tokens_refresh_view, name="token_refresh_view"),
    path(route="reset", view=reset_password_view, name="reset_password_view"),
    path(route="confirm_login", view=confirm_login_view, name="confirm_login_view"),
    # Восстановление пароля
]
