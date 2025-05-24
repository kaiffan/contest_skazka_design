from typing import NoReturn
from config.settings import get_settings

settings = get_settings()


def set_refresh_cookie(response, value) -> NoReturn:
    response.set_cookie(
        key=settings.token_credentials.REFRESH_COOKIE_KEY,
        value=value,
        httponly=True,
        secure=False,
        samesite="Lax",
        path=settings.token_credentials.REFRESH_COOKIE_PATH,
        max_age=settings.token_credentials.REFRESH_COOKIE_MAX_AGE,
    )


def delete_refresh_cookie(response) -> NoReturn:
    response.delete_cookie(
        key=settings.token_credentials.REFRESH_COOKIE_KEY,
        path=settings.token_credentials.REFRESH_COOKIE_PATH,
    )
