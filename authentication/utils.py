from datetime import timedelta
from typing import NoReturn
from django.utils import timezone

from django.db import transaction

from authentication.email import send_confirmation_email
from authentication.models import Users
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


def send_confirmation_code(
    user: Users, session_id: str
) -> tuple[None, dict[str, str]] | tuple[EmailConfirmationLogin, None]:
    with transaction.atomic():
        confirmation = EmailConfirmationLogin.objects.filter(
            user=user, session_id=session_id, is_used=False
        ).first()

        now = timezone.now()

        if confirmation and confirmation.locked_until:
            if confirmation.locked_until > now:
                return None, {
                    "error": f"Слишком много попыток. Повторите позже — после {confirmation.locked_until.strftime('%H:%M:%S')}"
                }
            else:
                confirmation.attempt_number = 0
                confirmation.locked_until = None
                confirmation.save(update_fields=["attempt_number", "locked_until"])

        code, code_hash = EmailConfirmationLogin.generate_code()
        if not confirmation:
            confirmation = EmailConfirmationLogin.objects.create(
                user=user,
                code_hash=code_hash,
                session_id=session_id,
                attempt_number=1,
            )
            send_confirmation_email(user_email=user.email, code=code)
            return confirmation, None

        if confirmation.attempt_number >= 3:
            confirmation.locked_until = now + timedelta(minutes=15)
            confirmation.save()
            return None, {
                "error": f"Превышено количество попыток. Блокировка до {confirmation.locked_until.strftime('%H:%M:%S')}"
            }

        confirmation.code_hash = code_hash
        confirmation.attempt_number += 1
        confirmation.save()

        send_confirmation_email(user_email=user.email, code=code)

        return confirmation, None
