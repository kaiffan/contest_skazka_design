from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from authentication.models import Users
from authentication.permissions import IsAdminSystemPermission
from block_user.models import UserBlock
from block_user.paginator import BlockUserPagination
from block_user.permissions import IsNotBlockUserPermission
from block_user.serializers import (
    BlockUserSerializer,
    UnblockUserSerializer,
    AllBlockUsersSerializer,
)
from users.serializers import UserParticipantSerializer


@extend_schema(
    summary="Блокировка пользователя",
    description="Позволяет администратору заблокировать пользователя на определённый срок с указанием причины.",
    request=BlockUserSerializer,
    responses={
        200: {"type": "object", "properties": {"success": {"type": "string"}}},
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
        404: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={
                "user_id": 123,
                "reason_blocked": "Нарушение правил",
                "blocked_until": "2025-12-31T23:59:59Z",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Успешная блокировка",
            value={"success": "Пользователь успешно заблокирован"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Пользователь не найден",
            value={"error": "Пользователь не найден."},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Уже заблокирован",
            value={"error": "Этот пользователь уже заблокирован"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsAdminSystemPermission,
        IsNotBlockUserPermission,
    ]
)
def block_user_view(request: Request) -> Response:
    serializer = BlockUserSerializer(
        data=request.data, context={"blocked_by_id": request.user.id}
    )
    if not serializer.is_valid(raise_exception=True):
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(
        data={"success": "Пользователь успешно заблокирован"}, status=status.HTTP_200_OK
    )


@extend_schema(
    summary="Разблокировка пользователя",
    description="Позволяет администратору разблокировать ранее заблокированного пользователя.",
    request=UnblockUserSerializer,
    responses={
        200: {"type": "object", "properties": {"success": {"type": "string"}}},
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
        404: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример запроса", value={"user_id": 123}, request_only=True
        ),
        OpenApiExample(
            name="Успешная разблокировка",
            value={"success": "Пользователь успешно разблокирован"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Пользователь не найден",
            value={"error": "Заблокированный пользователь не найден в системе."},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsAdminSystemPermission,
        IsNotBlockUserPermission,
    ]
)
def unblock_user_view(request: Request) -> Response:
    serializer = UnblockUserSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(
        data={"success": "Пользователь успешно разблокирован"},
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Получить всех заблокированных пользователей",
    description="Возвращает список всех текущих заблокированных пользователей с информацией о дате, причине и кем заблокирован.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location="query",
            description="Номер страницы",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location="query",
            description="Количество элементов на странице",
        ),
    ],
    examples=[
        OpenApiExample(
            name="Пример ответа",
            value={
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "user_id": 123,
                        "user_email": "user@example.com",
                        "user_fio": "Иванов Иван",
                        "blocked_by_fio": "Петров Пётр",
                        "blocked_until": "2025-12-31T23:59:59Z",
                        "is_blocked": True,
                    },
                    {
                        "user_id": 456,
                        "user_email": "another@example.com",
                        "user_fio": "Сидоров Сидор",
                        "blocked_by_fio": "Петров Пётр",
                        "blocked_until": "2025-12-31T23:59:59Z",
                        "is_blocked": True,
                    },
                ],
            },
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsAdminSystemPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_blocked_users_view(request: Request) -> Response:
    queryset = (
        UserBlock.objects.prefetch_related("user", "blocked_by")
        .filter(is_blocked=True)
        .all()
    )

    paginator = BlockUserPagination()
    result_page = paginator.paginate_queryset(queryset=queryset, request=request)

    serializer = AllBlockUsersSerializer(instance=result_page, many=True)
    return paginator.get_paginated_response(data=serializer.data)


@extend_schema(
    summary="Получить список незаблокированных пользователей",
    description="Возвращает список пользователей, которые не заблокированы в системе.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location="query",
            description="Номер страницы",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location="query",
            description="Количество элементов на странице",
        ),
    ],
    examples=[
        OpenApiExample(
            name="Пример ответа",
            value={
                "count": 5,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": 789,
                        "first_name": "Анна",
                        "last_name": "Иванова",
                        "email": "anna@example.com",
                    }
                ],
            },
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsAdminSystemPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_users_view(request: Request) -> Response:
    blocked_user_ids = UserBlock.objects.filter(is_blocked=True).values_list(
        "user_id", flat=True
    )
    user_list = (
        Users.objects.all().exclude(id=request.user.id).exclude(id__in=blocked_user_ids)
    )

    paginator = BlockUserPagination()
    users_page = paginator.paginate_queryset(queryset=user_list, request=request)

    serializer = UserParticipantSerializer(instance=users_page, many=True)
    return paginator.get_paginated_response(data=serializer.data)
