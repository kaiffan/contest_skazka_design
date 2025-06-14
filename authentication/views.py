from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiParameter
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from authentication.serializers import (
    RegistrationSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetSerializer,
)
from block_user.permissions import IsNotBlockUserPermission
from contest_backend.settings import settings

from authentication.throttle import CodeBasedThrottle, IpBasedThrottle
from authentication.utils import (
    set_refresh_cookie,
    delete_refresh_cookie,
    send_confirmation_code,
)
from email_confirmation.models import EmailConfirmationLogin
from django.utils import timezone


@extend_schema(
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя на основе предоставленной информации.",
    request=RegistrationSerializer,
    responses={
        201: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={
                "first_name": "Иван",
                "last_name": "Иванов",
                "email": "ivan@example.com",
                "birth_date": "1990-01-01",
                "password": "SecurePass123!",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Registration successful"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Email уже существует",
            value={"error": "A user with that email already exists."},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[AllowAny])
@throttle_classes(throttle_classes=[CodeBasedThrottle, IpBasedThrottle])
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


@extend_schema(
    summary="Вход пользователя",
    description="Авторизует пользователя по email и паролю. Отправляет код подтверждения на почту.",
    request=LoginSerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
        401: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={"email": "ivan@example.com", "password": "SecurePass123!"},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Код отправлен на почту"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Неверные учетные данные",
            value={"error": "A user with this email and password was not found."},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Пользователь не активирован",
            value={"error": "This user is not currently activated."},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[AllowAny])
@throttle_classes(throttle_classes=[CodeBasedThrottle, IpBasedThrottle])
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


@extend_schema(
    summary="Повторная отправка кода подтверждения",
    description="Отправляет повторный код подтверждения на email пользователя, если предыдущий истёк.",
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"detail": {"type": "string"}}},
        401: {"type": "object", "properties": {"error": {"type": "string"}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Код успешно отправлен повторно"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Сессия не найдена",
            value={"detail": "Нет активной сессии или попытки."},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Попытка не найдена",
            value={"detail": "Не найдено активной попытки подтверждения."},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Код ещё не истёк",
            value={
                "error": "Предыдущий код ещё не истёк. Пожалуйста, подождите и отправьте запрос после истечения!"
            },
            response_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes(throttle_classes=[IpBasedThrottle])
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


@extend_schema(
    summary="Подтверждение входа по коду",
    description="Подтверждает вход пользователя по одноразовому коду из email.",
    parameters=[
        OpenApiParameter(
            name="code",
            type=OpenApiTypes.STR,
            location="path",
            description="Одноразовый код подтверждения (обычно 6 цифр)",
        )
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "token_type": {"type": "string"},
                "access_token": {"type": "string"},
            },
        },
        400: {
            "type": "object",
            "properties": {"detail": {"type": "string"}, "error": {"type": "string"}},
        },
        401: {
            "type": "object",
            "properties": {"detail": {"type": "string"}, "error": {"type": "string"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса", value={"code": "123456"}, request_only=True
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={
                "message": "Вход подтверждён.",
                "token_type": "Bearer",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx",
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Неверный код",
            value={"detail": "Неверный или использованный код подтверждения."},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Код истёк",
            value={"detail": "Код подтверждения истёк."},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Код не указан",
            value={"detail": "Код подтверждения обязателен."},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[AllowAny])
@throttle_classes(throttle_classes=[IpBasedThrottle])
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
        confirmation.used_at = timezone.now()
        confirmation.save(update_fields=["is_used", "used_at"])

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


@extend_schema(
    summary="Обновление токенов через Cookie",
    description="Обновляет access и refresh токены на основе refresh_token из кук.",
    request=None,
    responses={
        200: {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "message": {"type": "string"},
            },
        },
        400: {
            "description": "Ошибка валидации или отсутствующий токен",
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
        401: {
            "description": "Неверный или истёкший refresh token",
            "type": "object",
            "properties": {"error": {"type": "string"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value={
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx",
                "message": "Refresh successful",
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Refresh token отсутствует",
            value={"error": "Refresh token is missing"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Неверный refresh token",
            value={"error": "Token is invalid or expired"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        AllowAny,
    ]
)
@throttle_classes(throttle_classes=[IpBasedThrottle])
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


@extend_schema(
    summary="Выход пользователя (Logout)",
    description="Производит выход пользователя, удаляя refresh-токен из кук и устанавливая флаг подтверждения email в False.",
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
        401: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Успешный выход",
            value={"message": "Logout successful"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Refresh token не найден",
            value={"error": "Refresh token not found"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
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


@extend_schema(
    summary="Смена пароля",
    description="Изменяет пароль текущего пользователя после валидации данных.",
    request="PasswordResetSerializer",
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={
                "password": "new_secure_password123",
                "password_confirm": "new_secure_password123",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Успешная смена пароля",
            value={"message": "Пароль успешно изменён."},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Пароли не совпадают",
            value={
                "errors": {"non_field_errors": ["Passwords do not match."]},
                "error": "Passwords do not match.",
            },
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["PUT"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
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
