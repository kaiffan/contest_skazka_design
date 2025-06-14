from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from applications.enums import ApplicationStatus
from applications.filters import ApplicationFilter
from applications.models import Applications
from applications.paginator import ApplicationPaginator
from applications.serializers import (
    SendApplicationsSerializer,
    ApproveApplicationSerializer,
    RejectApplicationSerializer,
    ApplicationSerializer,
    ApplicationWithCriteriaSerializer,
    UpdateApplicationSerializer,
)
from block_user.permissions import IsNotBlockUserPermission
from contest_stage.permissions import CanSubmitApplicationPermission
from participants.permissions import (
    IsContestJuryPermission,
    IsOrgCommitteePermission,
    IsContestMemberPermission,
)


def get_filtered_applications(contest_id: str, status_filter: str):
    return Applications.objects.filter(
        contest_id=contest_id, status=status_filter
    ).all()


def get_applications_by_status(request: Request, status_filter: str) -> Response:
    paginator = ApplicationPaginator()
    queryset = get_filtered_applications(
        contest_id=request.contest_id, status_filter=status_filter
    )
    page = paginator.paginate_queryset(queryset=queryset, request=request)
    serializer = ApplicationSerializer(page, many=True)

    return paginator.get_paginated_response(data=serializer.data)


@extend_schema(
    summary="Отправка новой заявки",
    description="Создание заявки на участие в конкурсе с указанием номинации и данных работы.",
    request=SendApplicationsSerializer,
    responses={
        201: SendApplicationsSerializer,
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
        404: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример заявки",
            value={
                "name": "Моя творческая работа",
                "annotation": "Это описание моей лучшей работы",
                "link_to_work": "https://example.com/work",
                "nomination_id": 1,
                "contest_id": 5,
            },
            request_only=True,
            media_type="application/json",
        ),
        OpenApiExample(
            name="Ошибка: Заявка уже существует",
            value={"error": "Application already exists"},
            response_only=True,
            media_type="application/json",
        ),
        OpenApiExample(
            name="Ошибка: Конкурс не найден",
            value={"error": "Contest does not exist"},
            response_only=True,
            media_type="application/json",
        ),
        OpenApiExample(
            name="Ошибка: Неверные данные",
            value={
                "error": "Invalid data",
                "errors": {
                    "name": ["Обязательное поле."],
                    "nomination_id": ["Неверный тип."],
                },
            },
            response_only=True,
            media_type="application/json",
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsNotBlockUserPermission,
        CanSubmitApplicationPermission,
    ]
)
def send_applications_view(request: Request) -> Response:
    serializer = SendApplicationsSerializer(
        data=request.data, context={"user": request.user}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Одобрение нескольких заявок",
    description="Одобрить несколько заявок по их ID. Также создаёт участника конкурса.",
    request=ApproveApplicationSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "detail": {"type": "string"},
                "ids": {"type": "array", "items": {"type": "integer"}},
            },
        },
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса (одобрение)",
            value={"application_ids": [1, 2, 3]},
            request_only=True,
        ),
        OpenApiExample(
            name="Пример ответа",
            value={"detail": "3 заявки одобрены", "ids": [1, 2, 3]},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Неверный ID заявки",
            value={"error": "Заявка с ID 999 не найдена"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["PUT"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsNotBlockUserPermission,
        CanSubmitApplicationPermission,
    ]
)
def approve_application_view(request: Request) -> Response:
    serializer = ApproveApplicationSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    approved_apps = serializer.save()

    return Response(
        data={
            "detail": f"{len(approved_apps)} заявок одобрено",
            "ids": [application.id for application in approved_apps],
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Отклонение одной заявки",
    description="Отклоняет одну заявку по ID с указанием причины",
    request=RejectApplicationSerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса (отклонение)",
            value={
                "application_id": 1,
                "rejection_reason": "Не соответствует требованиям",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Пример ответа",
            value={"message": "Application rejected"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Заявка не найдена",
            value={"error": "Заявка не найдена"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["PATCH"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsNotBlockUserPermission,
        CanSubmitApplicationPermission,
    ]
)
def reject_application_view(request: Request) -> Response:
    serializer = RejectApplicationSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(
        data={
            "message": "Application rejected",
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Получить все заявки на рассмотрении",
    description="Возвращает список заявок со статусом 'ожидает рассмотрения'. Поддерживает пагинацию.",
    parameters=[
        OpenApiParameter(
            name="page", type=int, location="query", description="Номер страницы"
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            location="query",
            description="Количество элементов на странице",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "format": "uri"},
                "previous": {"type": "string", "format": "uri"},
            },
            "description": "Пагинированный список заявок",
        }
    },
    examples=[
        OpenApiExample(
            name="Пример успешного ответа",
            value={
                "count": 5,
                "next": "https://skazka-design.ru/applications/?page=2",
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "name": "Заявка 1",
                        "status": "pending",
                        "contest_title": "Конкурс 1",
                        "nomination_name": "Лучший фильм",
                        "age_category": "Дети",
                        "user_id": 1001,
                    },
                    {
                        "id": 2,
                        "name": "Заявка 2",
                        "status": "pending",
                        "contest_title": "Конкурс 1",
                        "nomination_name": "Лучший фильм",
                        "age_category": "Подростки",
                        "user_id": 1002,
                    },
                ],
            },
            response_only=True,
            media_type="application/json",
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_applications_view(request: Request) -> Response:
    return get_applications_by_status(
        request=request, status_filter=ApplicationStatus.pending.value
    )


@extend_schema(
    summary="Получить отклонённые заявки",
    description="Возвращает список заявок со статусом 'отклонено'. Поддерживает пагинацию.",
    parameters=[
        OpenApiParameter(
            name="page", type=int, location="query", description="Номер страницы"
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            location="query",
            description="Количество элементов на странице",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "format": "uri"},
                "previous": {"type": "string", "format": "uri"},
            },
            "description": "Пагинированный список отклонённых заявок",
        }
    },
    examples=[
        OpenApiExample(
            name="Пример успешного ответа",
            value={
                "count": 3,
                "next": None,
                "previous": "https://skazka-design.ru/applications/rejected/?page=1",
                "results": [
                    {
                        "id": 5,
                        "name": "Заявка 5",
                        "status": "rejected",
                        "rejection_reason": "Не соответствует требованиям",
                        "contest_title": "Конкурс 2",
                        "nomination_name": "Лучшая музыка",
                        "age_category": "Взрослые",
                        "user_id": 1005,
                    }
                ],
            },
            response_only=True,
            media_type="application/json",
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_applications_rejected_view(request: Request) -> Response:
    return get_applications_by_status(
        request=request, status_filter=ApplicationStatus.rejected.value
    )


@extend_schema(
    summary="Получить одобренные заявки",
    description="Возвращает список заявок со статусом 'одобрено'. Поддерживает пагинацию.",
    parameters=[
        OpenApiParameter(
            name="page", type=int, location="query", description="Номер страницы"
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            location="query",
            description="Количество элементов на странице",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "format": "uri"},
                "previous": {"type": "string", "format": "uri"},
            },
            "description": "Пагинированный список одобренных заявок",
        }
    },
    examples=[
        OpenApiExample(
            name="Пример успешного ответа",
            value={
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": 3,
                        "name": "Заявка 3",
                        "status": "accepted",
                        "contest_title": "Конкурс 1",
                        "nomination_name": "Лучший фильм",
                        "age_category": "Дети",
                        "user_id": 1003,
                    },
                    {
                        "id": 4,
                        "name": "Заявка 4",
                        "status": "accepted",
                        "contest_title": "Конкурс 1",
                        "nomination_name": "Лучший актер",
                        "age_category": "Подростки",
                        "user_id": 1004,
                    },
                ],
            },
            response_only=True,
            media_type="application/json",
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_applications_approved_view(request: Request) -> Response:
    return get_applications_by_status(
        request=request, status_filter=ApplicationStatus.accepted.value
    )


@extend_schema(
    summary="Получение заявки по ID",
    description="Возвращает подробную информацию о заявке, включая номинацию и критерии конкурса.",
    responses={
        200: ApplicationWithCriteriaSerializer,
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
        404: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример тела запроса", value={"application_id": 1}, request_only=True
        ),
        OpenApiExample(
            name="Пример успешного ответа",
            value={
                "id": 1,
                "name": "Моя работа",
                "link_to_work": "https://example.com/work",
                "annotation": "Описание работы",
                "status": "pending",
                "rejection_reason": None,
                "user_id": 123,
                "contest_id": 5,
                "nomination": {
                    "id": 1,
                    "contest_id": 5,
                    "nomination_id": 3,
                    "name": "Лучший фильм",
                },
                "criteria": [
                    {
                        "id": 1,
                        "contest_id": 5,
                        "criterion_id": 7,
                        "name": "Креативность",
                        "description": "Оценка оригинальности",
                    },
                    {
                        "id": 2,
                        "contest_id": 5,
                        "criterion_id": 8,
                        "name": "Техника исполнения",
                        "description": "Оценка мастерства",
                    },
                ],
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: application_id не передан",
            value={"error": "Application id not found"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Заявка не найдена",
            value={"error": "Application not found"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_application_view(request: Request) -> Response:
    application_id = request.data.get("application_id", None)

    if not application_id:
        return Response(
            data={"error": "Application id not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    application = Applications.objects.get(id=application_id)
    serializer = ApplicationWithCriteriaSerializer(instance=application)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получение заявок текущего пользователя",
    description="Возвращает список заявок текущего пользователя с поддержкой фильтрации и пагинации.",
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
        OpenApiParameter(
            name="contest_id",
            type=OpenApiTypes.INT,
            location="query",
            description="Фильтр по ID конкурса",
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location="query",
            description="Фильтр по статусу заявки (например: pending, accepted, rejected)",
        ),
        OpenApiParameter(
            name="nomination_id",
            type=OpenApiTypes.INT,
            location="query",
            description="Фильтр по ID номинации",
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "format": "uri"},
                "previous": {"type": "string", "format": "uri"},
            },
            "description": "Пагинированный список заявок пользователя",
        }
    },
    examples=[
        OpenApiExample(
            name="Пример успешного ответа",
            value={
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "name": "Заявка 1",
                        "status": "pending",
                        "contest_id": 5,
                        "user_id": 1001,
                    },
                    {
                        "id": 2,
                        "name": "Заявка 2",
                        "status": "accepted",
                        "contest_id": 6,
                        "user_id": 1001,
                    },
                ],
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Пример URL с фильтром",
            value=None,
            request_only=True,
            media_type="application/json",
            description="GET /api/v1/applications/user/?status=pending&page=1",
        ),
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_applications_user_view(request: Request) -> Response:
    user_applications = Applications.objects.filter(
        user_id=request.user.id, is_deleted=False
    ).all()

    application_filter = ApplicationFilter(data=request.GET, queryset=user_applications)

    paginator = ApplicationPaginator()

    paginated_queryset = paginator.paginate_queryset(
        queryset=application_filter.qs, request=request
    )
    serializer = ApplicationSerializer(instance=paginated_queryset, many=True)

    return paginator.get_paginated_response(data=serializer.data)


@extend_schema(
    summary="Обновление заявки",
    description="Обновляет существующую заявку по ID. После изменения статус автоматически устанавливается в 'ожидание'.",
    request=UpdateApplicationSerializer,
    responses={
        200: UpdateApplicationSerializer,
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
                "application_id": 1,
                "name": "Обновлённое название",
                "annotation": "Обновлённая аннотация",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Пример успешного ответа",
            value={
                "id": 1,
                "name": "Обновлённое название",
                "annotation": "Обновлённая аннотация",
                "link_to_work": "https://example.com/work",
                "status": "pending",
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Заявка не найдена",
            value={"error": "Application not found"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: application_id не передан",
            value={"error": "Application id not found"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["PATCH"])
@permission_classes(
    [
        IsAuthenticated,
        IsNotBlockUserPermission,
        IsContestMemberPermission,
        CanSubmitApplicationPermission,
    ]
)
def update_application_view(request: Request) -> Response:
    application_id = request.data.get("application_id")

    if not application_id:
        return Response(
            data={"error": "Application id not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        application = Applications.objects.get(id=application_id)
    except Applications.DoesNotExist:
        return Response(
            data={"error": "Application not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UpdateApplicationSerializer(
        instance=application, data=request.data, partial=True
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Удаление заявки (мягкое)",
    description="Мягко удаляет заявку по ID (устанавливает флаг is_deleted = True). Пользователь может удалить только свои заявки.",
    responses={
        200: {
            "description": "Заявка успешно удалена",
            "type": "object",
            "properties": {"message": {"type": "string"}},
        },
        400: {
            "description": "application_id не передан",
            "type": "object",
            "properties": {"error": {"type": "string"}},
        },
        403: {
            "description": "Пользователь не имеет прав на удаление этой заявки",
            "type": "object",
            "properties": {"error": {"type": "string"}},
        },
        404: {
            "description": "Заявка не найдена",
            "type": "object",
            "properties": {"error": {"type": "string"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса", value={"application_id": 1}, request_only=True
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"message": "Application successfully deleted"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: application_id не передан",
            value={"error": "Application id not found"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Заявка не найдена",
            value={"error": "Application not found"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Нет доступа",
            value={"error": "You do not have permission to delete this application"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["DELETE"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def delete_application_view(request: Request) -> Response:
    application_id = request.data.get("application_id")

    if not application_id:
        return Response(
            data={"error": "Application id not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        application = Applications.objects.get(id=application_id)
    except Applications.DoesNotExist:
        return Response(
            data={"error": "Application not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if application.user != request.user:
        return Response(
            data={"error": "You do not have permission to delete this application"},
            status=status.HTTP_403_FORBIDDEN,
        )

    application.is_deleted = True
    application.save(update_fields=["is_deleted"])

    return Response(
        data={"message": "Application successfully deleted"},
        status=status.HTTP_200_OK,
    )
