from typing import NoReturn

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from authentication.email import send_confirmation_email
from config.settings import get_settings
from email_confirmation.models import EmailConfirmationLogin

settings = get_settings()


def set_refresh_cookie(response, value) -> NoReturn:
    response.set_cookie(
        key=settings.token_credentials.REFRESH_COOKIE_KEY,
        value=value,
        httponly=True,
        secure=True,
        samesite="None",
        path=settings.token_credentials.REFRESH_COOKIE_PATH,
        max_age=settings.token_credentials.REFRESH_COOKIE_MAX_AGE,
    )


def delete_refresh_cookie(response) -> NoReturn:
    response.delete_cookie(
        key=settings.token_credentials.REFRESH_COOKIE_KEY,
        path=settings.token_credentials.REFRESH_COOKIE_PATH,
    )


def send_confirmation_code(user, session_id, resend=False):
    with transaction.atomic():
        confirmation = EmailConfirmationLogin.objects.filter(
            user=user,
            session_id=session_id,
            is_used=False
        ).first()

        if resend:
            EmailConfirmationLogin.objects.filter(
                user=user, session_id=session_id, is_used=False
            ).delete()

        attempt_number = (
            EmailConfirmationLogin.objects.filter(session_id=session_id).count() + 1
        )

        if attempt_number > 3:
            return None, {"error": "Превышено количество попыток"}
        

        code, code_hash = EmailConfirmationLogin.generate_code()
        confirmation = EmailConfirmationLogin.objects.create(
            user=user,
            code_hash=code_hash,
            session_id=session_id,
            attempt_number=attempt_number,
        )

        send_confirmation_email(user_email=user.email, code=code)

        return confirmation, None
