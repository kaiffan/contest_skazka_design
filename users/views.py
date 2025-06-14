from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from authentication.models import Users
from block_user.permissions import IsNotBlockUserPermission
from participants.permissions import IsContestOwnerPermission, IsOrgCommitteePermission

from users.serializers import (
    ContestDataUpdateSerializer,
    UserDataPatchSerializer,
    UserFullDataSerializer,
    UserShortDataSerializer,
    UserCompetenciesSerializer,
    UserParticipantSerializer,
)


@extend_schema(
    summary="Обновление данных конкурса",
    description="Позволяет пользователю обновить свои данные, связанные с конкурсом (например: образование/работа, компетенции).",
    request=ContestDataUpdateSerializer,
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
                "competencies": ["фильмы", "музыка"],
                "education_or_work": "Кинодраматург",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={
                "message": "Данные успешно обновлены",
                "data": {
                    "competencies": ["фильмы"],
                    "education_or_work": "Кинодраматург",
                },
            },
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["PUT"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def contest_data_update_view(request: Request) -> Response:
    serializer = ContestDataUpdateSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.update_user_data(user=request.user)

    return Response(
        data={"message": "Данные успешно обновлены", "data": serializer.data},
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Частичное обновление данных пользователя",
    description="Позволяет пользователю обновить отдельные поля своих данных (например: email, имя).",
    request=UserDataPatchSerializer,
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
            value={"first_name": "Петр", "last_name": "Иванов"},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Данные успешно обновлены"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["PATCH"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def user_data_update_view(request: Request) -> Response:
    serializer = UserDataPatchSerializer(
        data=request.data, instance=request.user, partial=True
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.update(instance=request.user, validated_data=serializer.validated_data)

    return Response(
        data={"message": "Данные успешно обновлены"},
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Получение полных данных пользователя",
    description="Возвращает все данные текущего пользователя, включая компетенции.",
    responses={200: UserFullDataSerializer},
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def user_data_get_view(request: Request) -> Response:
    serializer = UserFullDataSerializer(instance=request.user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение кратких данных пользователя",
    description="Возвращает основные данные пользователя: имя, фамилия, аватар.",
    responses={200: UserShortDataSerializer},
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def user_short_data_get_view(request: Request) -> Response:
    serializer = UserShortDataSerializer(instance=request.user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение всех пользователей",
    description="Возвращает список всех пользователей системы. Можно фильтровать по email.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location="query",
            description="Фильтрация по email",
        )
    ],
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value=[
                {"id": 1, "email": "user1@example.com"},
                {"id": 2, "email": "user2@example.com"},
            ],
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsOrgCommitteePermission,
        IsNotBlockUserPermission,
    ]
)
def all_users_view(request: Request) -> Response:
    search: str = request.data.get("search", None)

    queryset = Users.objects.all()

    if search:
        queryset = queryset.filter(email__icontains=search)

    serializer = UserParticipantSerializer(instance=queryset, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение компетенций пользователя",
    description="Возвращает информацию о компетенциях пользователя по email.",
    parameters=[
        OpenApiParameter(
            name="email",
            type=OpenApiTypes.STR,
            location="path",
            description="Email пользователя",
        )
    ],
    responses={200: UserCompetenciesSerializer},
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={"email": "user@example.com"},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={
                "id": 1,
                "first_name": "Иван",
                "last_name": "Иванов",
                "email": "user@example.com",
                "competencies": [{"name": "Кино"}],
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Email не указан",
            value={"error": "Not exists email"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def user_competencies_jury_view(request: Request) -> Response:
    email = request.data.get("email", None)

    if not email:
        return Response(data={"error": "Not exists email"})

    user = Users.objects.get(email=email)
    serializer = UserCompetenciesSerializer(instance=user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
