from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from authentication.serializers import (
    RegistrationSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetSerializer,
)
from contest_backend.settings import settings

# from authentication.throttle import CodeBasedThrottle, IpBasedThrottle
from authentication.utils import (
    set_refresh_cookie,
    delete_refresh_cookie,
    send_confirmation_code,
)
from email_confirmation.models import EmailConfirmationLogin


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        AllowAny,
    ]
)
def registration_view(request: Request) -> Response:
    serializer = RegistrationSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(
        data={
            "message": "Registration successful",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[AllowAny])
def login_view(request: Request) -> Response:
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data

    session_id = EmailConfirmationLogin.generate_session_id()
    request.session["email_login_session_id"] = session_id

    confirmation, error = send_confirmation_code(user=user, session_id=session_id)
    if error:
        return Response(data=error, status=status.HTTP_401_UNAUTHORIZED)

    request.session["login_attempt"] = confirmation.id
    request.session["session_id"] = session_id
    request.session.save()

    return Response(
        data={"message": "Код отправлен на почту"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_code_view(request: Request) -> Response:
    session_id = request.session.get("email_login_session_id")
    attempt_id = request.session.get("login_attempt")

    if not session_id or not attempt_id:
        return Response(
            data={"detail": "Нет активной сессии или попытки."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        confirmation = EmailConfirmationLogin.objects.select_related("user").get(
            id=attempt_id, session_id=session_id, is_used=False
        )

        if not confirmation.is_expired():
            return Response(
                data={
                    "error": "Предыдущий код ещё не истёк. Пожалуйста, подождите и отправьте запрос после истечения!"
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        _, error = send_confirmation_code(confirmation.user, session_id)
        if error:
            return Response(data=error, status=status.HTTP_401_UNAUTHORIZED)

    except EmailConfirmationLogin.DoesNotExist:
        return Response(
            data={"detail": "Не найдено активной попытки подтверждения."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        data={"message": "Код успешно отправлен повторно"}, status=status.HTTP_200_OK
    )


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[AllowAny])
# @throttle_classes(throttle_classes=[CodeBasedThrottle, IpBasedThrottle])
def confirm_login_view(request: Request) -> Response:
    code = request.data.get("code", None)
    attempt_id = request.session.get("login_attempt", None)
    session_id = request.session.get("email_login_session_id", None)

    if not code:
        return Response(
            data={"detail": "Код подтверждения обязателен."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not attempt_id or not session_id:
        return Response(
            data={"detail": "Сессия не найдена или код попытки не указан."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(code) != settings.email_credentials.CODE_DIGITS:
        return Response(
            data={"detail": "Неверная длина кода подтверждения."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code_hash = EmailConfirmationLogin.hash_code(code=code)

    try:
        confirmation = EmailConfirmationLogin.objects.select_related("user").get(
            id=attempt_id,
            session_id=session_id,
            code_hash=code_hash,
            is_used=False,
        )
    except EmailConfirmationLogin.DoesNotExist:
        return Response(
            data={"detail": "Неверный или использованный код подтверждения."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if confirmation.is_expired():
        return Response(
            data={"detail": "Код подтверждения истёк."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    with transaction.atomic():
        confirmation.is_used = True
        confirmation.save(update_fields=["is_used"])

        user = confirmation.user
        user.is_email_confirmed = True
        user.save(update_fields=["is_email_confirmed"])

    request.session.pop("login_attempt", None)
    request.session.pop("email_login_session_id", None)

    response = Response(
        data={
            "message": "Вход подтверждён.",
            "token_type": "Bearer",
            "access_token": user.tokens.get("access"),
        },
        status=status.HTTP_200_OK,
    )
    set_refresh_cookie(response=response, value=user.tokens.get("refresh"))

    return response


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        AllowAny,
    ]
)
# @throttle_classes(throttle_classes=[IpBasedThrottle])
def cookie_tokens_refresh_view(request) -> Response:
    refresh_token: str = request.COOKIES.get("refresh_token", None)

    if not refresh_token:
        raise ValidationError("Refresh token is missing")

    token_refresh_serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

    if not token_refresh_serializer.is_valid(raise_exception=True):
        return Response(
            token_refresh_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    new_access_token: str = token_refresh_serializer.validated_data.get("access")
    new_refresh_token: str = token_refresh_serializer.validated_data.get("refresh")

    response: Response = Response(
        data={
            "access_token": new_access_token,
            "message": "Refresh successful",
        },
        status=status.HTTP_200_OK,
    )

    delete_refresh_cookie(response=response)
    set_refresh_cookie(response=response, value=new_refresh_token)

    return response


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
    ]
)
def logout_view(request: Request) -> Response:
    refresh_token: str = request.COOKIES.get("refresh_token")

    if not refresh_token:
        raise ValidationError("Refresh token not found")

    serializer = LogoutSerializer(data={}, context={"refresh_token": refresh_token})

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    request.user.is_email_confirmed = False

    response = Response(
        data={
            "message": "Logout successful",
        },
        status=status.HTTP_200_OK,
    )
    delete_refresh_cookie(response=response)
    return response


@api_view(http_method_names=["PUT"])
@permission_classes(permission_classes=[IsAuthenticated])
def reset_password_view(request: Request) -> Response:
    serializer = PasswordResetSerializer(
        data=request.data, context={"user": request.user}
    )
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.update(instance=request.user, validated_data=serializer.validated_data)
    return Response(
        data={"message": "Пароль успешно изменён."}, status=status.HTTP_200_OK
    )
