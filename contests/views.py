from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request

from authentication.permissions import IsAdminSystemPermission
from block_user.permissions import IsNotBlockUserPermission
from contests.filter import ContestFilter
from contests.models import Contest
from contests.paginator import ContestPaginator
from contests.serializers import (
    CreateBaseContestSerializer,
    UpdateBaseContestSerializer,
    ContestByIdSerializer,
    ContestAllSerializer,
    ContestAllOwnerSerializer,
    ContestAllJurySerializer,
)
from participants.enums import ParticipantRole
from participants.permissions import IsContestOwnerPermission


@extend_schema(
    summary="Создание нового конкурса",
    description="Позволяет пользователю создать новый конкурс с основными данными.",
    request=CreateBaseContestSerializer,
    responses={
        201: {
            "type": "object",
            "properties": {
                "contest_id": {"type": "integer"},
                "message": {"type": "string"},
            },
        },
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={
                "title": "Конкурс талантов",
                "description": "Ежегодный конкурс для молодых талантов",
                "organizer": "Министерство культуры",
                "contest_category_name": "Искусство",
                "age_category": [1, 2],
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"contest_id": 1, "message": "Contest created successfully"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def create_contest_view(request: Request) -> Response:
    serializer = CreateBaseContestSerializer(
        data=request.data, context={"user_id": request.user.id}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    contest = serializer.create(validated_data=serializer.validated_data)

    return Response(
        data={"contest_id": contest.id, "message": "Contest created successfully"},
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    summary="Обновление данных о конкурсе",
    description="Частично обновляет данные о конкурсе по ID из URL или контекста.",
    request=UpdateBaseContestSerializer,
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
            value={"title": "Новое название", "description": "Обновленное описание"},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Contest successfully update"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["PATCH"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsNotBlockUserPermission,
    ]
)
def update_contest_view(request: Request) -> Response:
    serializer = UpdateBaseContestSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    contest = get_object_or_404(Contest, id=request.contest_id)

    serializer.update(instance=contest, validated_data=serializer.validated_data)

    return Response(
        data={"message": "Contest successfully update"}, status=status.HTTP_200_OK
    )


@extend_schema(
    summary="Публикация конкурса",
    description="Устанавливает флаг is_published=True у конкурса.",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Contest successfully published"},
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[IsAdminSystemPermission, IsNotBlockUserPermission]
)
def publish_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    contest.is_published = True
    contest.is_draft = False
    contest.save(update_fields=["is_published"])

    return Response(
        data={"message": "Contest successfully published"}, status=status.HTTP_200_OK
    )


@extend_schema(
    summary="Отмена публикации конкурса",
    description="Убирает флаг is_published у конкурса.",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Contest successfully deleted"},
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["DELETE"])
@permission_classes(
    permission_classes=[IsAdminSystemPermission, IsNotBlockUserPermission]
)
def reject_publish_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    contest.is_published = False
    contest.save(update_fields=["is_published"])

    return Response(
        data={"message": "Contest successfully deleted"}, status=status.HTTP_200_OK
    )


@extend_schema(
    summary="Получение всех опубликованных конкурсов",
    description="Возвращает список всех опубликованных конкурсов.",
    responses={200: ContestAllSerializer},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value=[
                {
                    "id": 1,
                    "title": "Конкурс талантов",
                    "avatar": "https://example.com/avatar.jpg",
                    "contest_category": {"name": "Искусство"},
                    "contest_stage": "registration",
                }
            ],
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[IsAdminSystemPermission, IsNotBlockUserPermission]
)
def get_published_contest_view(request: Request) -> Response:
    contest_list = Contest.objects.all().filter(is_published=True)

    serializer = ContestAllSerializer(instance=contest_list, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение данных конкурса по ID",
    description="Возвращает полную информацию о конкурсе (для всех пользователей).",
    responses={200: ContestByIdSerializer},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value={
                "id": 1,
                "title": "Конкурс талантов",
                "description": "Ежегодный конкурс для молодых талантов",
                "link_to_rules": "https://example.com/rules",
                "avatar": "https://example.com/avatar.jpg",
                "organizer": "Министерство культуры",
                "is_draft": False,
                "is_deleted": False,
                "is_published": True,
                "nomination": [{"name": "Лучший фильм"}],
                "criteria": [
                    {"name": "Креативность", "description": "Оценка оригинальности"}
                ],
                "age_categories": [{"name": "Дети"}],
                "contest_stage": ["registration"],
                "jury": [],
                "org_committee": [],
                "file_constraint": {"max_size": "10MB"},
                "contest_category": {"name": "Искусство"},
                "prizes": "Призы за победу",
                "contacts_for_participants": "email@example.com",
            },
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_contest_by_id_view(request: Request) -> Response:
    instance = Contest.objects.prefetch_related(
        "criteria",
        "nominations",
        "age_category",
        "participants",
        "contest_stage",
        "file_constraint",
    ).get(id=request.contest_id)

    serializer = ContestByIdSerializer(instance=instance)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение данных конкурса (только для владельца)",
    description="Возвращает полную информацию о конкурсе только для его владельца.",
    responses={200: ContestByIdSerializer},
    examples=[
        OpenApiExample(
            name="Успешный ответ (владелец)",
            value={
                "id": 1,
                "title": "Конкурс талантов",
                "description": "Ежегодный конкурс для молодых талантов",
                "organizer": "Минкультуры",
                "contest_category": {"name": "Искусство"},
                "age_categories": [{"name": "Дети"}],
                "contest_stage": ["registration"],
            },
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsNotBlockUserPermission,
    ]
)
def get_contest_by_id_owner_view(request: Request) -> Response:
    instance = Contest.objects.prefetch_related(
        "criteria",
        "nominations",
        "age_category",
        "participants",
        "contest_stage",
        "file_constraint",
    ).get(id=request.contest_id)

    serializer = ContestByIdSerializer(instance=instance)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение всех опубликованных конкурсов",
    description="Возвращает список всех опубликованных и не удалённых конкурсов (без прав доступа).",
    responses={200: ContestAllSerializer},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value=[
                {
                    "id": 1,
                    "title": "Конкурс талантов",
                    "avatar": "https://example.com/avatar.jpg",
                    "contest_category": {"name": "Искусство"},
                    "contest_stage": ["registration"],
                }
            ],
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_all_contests_not_permissions_view(request: Request) -> Response:
    contest_list = Contest.objects.filter(is_published=True, is_deleted=False).all()

    serializer = ContestAllSerializer(instance=contest_list, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение списка опубликованных конкурсов",
    description="Возвращает список всех опубликованных конкурсов с возможностью фильтрации по названию, возрастной категории и этапу.",
    parameters=[
        OpenApiParameter(
            name="contest_title",
            type=OpenApiTypes.STR,
            location="query",
            description="Фильтрация по части названия конкурса",
        ),
        OpenApiParameter(
            name="age_category",
            type=int,
            location="query",
            description="Фильтрация по ID возрастной категории (можно несколько)",
        ),
        OpenApiParameter(
            name="contest_stage",
            type=int,
            location="query",
            description="Фильтрация по ID этапа конкурса (можно несколько)",
        ),
    ],
    responses={200: ContestAllSerializer},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value=[
                {
                    "id": 1,
                    "title": "Конкурс талантов",
                    "avatar": "https://example.com/avatar.jpg",
                    "contest_category": {"name": "Искусство"},
                    "contest_stage": ["registration"],
                },
                {
                    "id": 2,
                    "title": "Музыкальный конкурс",
                    "avatar": "https://example.com/music.jpg",
                    "contest_category": {"name": "Музыка"},
                    "contest_stage": ["submission", "review"],
                },
            ],
            response_only=True,
            media_type="application/json",
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_all_contests_view(request: Request) -> Response:
    contest_list = (
        Contest.objects.filter(is_published=True, is_deleted=False).all().order_by("id")
    )

    contest_filter = ContestFilter(data=request.GET, queryset=contest_list)

    paginator = ContestPaginator()
    paginated_queryset = paginator.paginate_queryset(
        queryset=contest_filter.qs, request=request
    )

    serializer = ContestAllSerializer(instance=paginated_queryset, many=True)

    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    summary="Получение всех конкурсов (владелец)",
    description="Возвращает список всех конкурсов, где пользователь является владельцем.",
    responses={200: ContestAllOwnerSerializer},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value=[
                {
                    "id": 1,
                    "title": "Конкурс талантов",
                    "avatar": "https://example.com/contest.jpg",
                    "count_application": 5,
                    "count_jury": 3,
                    "is_draft": False,
                    "is_published": True,
                    "is_deleted": False,
                }
            ],
            response_only=True,
            media_type="application/json",
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_all_contests_owner_view(request: Request) -> Response:
    contests = Contest.objects.filter(
        participant__user_id=request.user.id,
        participant__role=ParticipantRole.owner.value,
        is_deleted=False,
    ).distinct()

    serializer = ContestAllOwnerSerializer(instance=contests, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение всех конкурсов (жюри)",
    description="Возвращает список всех конкурсов, в которых пользователь состоит в роли жюри.",
    responses={200: ContestAllJurySerializer(many=True)},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value=[
                {
                    "id": 1,
                    "title": "Конкурс талантов",
                    "avatar": "https://example.com/contest.jpg",
                    "current_stage": "registration",
                    "count_application": 5,
                }
            ],
            response_only=True,
            media_type="application/json",
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_all_contests_jury_view(request: Request) -> Response:
    conntests = Contest.objects.filter(
        participant__user_id=request.user.id,
        participant__role=ParticipantRole.jury.value,
    )

    serializer = ContestAllJurySerializer(instance=conntests, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
