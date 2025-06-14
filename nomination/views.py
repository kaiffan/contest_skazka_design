from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django.core.cache import cache

from block_user.permissions import IsNotBlockUserPermission
from contests.models import Contest
from contests.serializers import ContestChangeNominationSerializer
from nomination.models import Nominations
from nomination.pagginator import NominationsPaginator
from nomination.serializers import NominationsSerializer
from participants.permissions import IsContestOwnerPermission


@extend_schema(
    summary="Получение всех номинаций",
    description="Возвращает список всех номинаций. Можно фильтровать по имени через параметр `search`.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location="query",
            description="Поиск по названию номинации",
        )
    ],
    responses={200: NominationsSerializer(many=True)},
    examples=[
        OpenApiExample(
            name="Успешный ответ",
            value={
                "data": [
                    {"id": 1, "name": "Лучший фильм"},
                    {"id": 2, "name": "Лучшая музыка"},
                ],
                "message": "All names by фильм",
            },
            response_only=True,
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_all_nominations(request: Request) -> Response:
    cache_key = f"nominations_all_{request.query_params.get('search', 'all')}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(data=cached_data, status=status.HTTP_200_OK)

    queryset = Nominations.objects.only("name").all()

    search = request.query_params.get("search", None)

    if search:
        queryset = queryset.filter(name__icontains=search)

    paginator = NominationsPaginator()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    serializer = NominationsSerializer(instance=paginated_queryset, many=True)
    response_data = {
        "data": serializer.data,
        "message": f"All names by {search}" if search else "All nominations",
    }

    cache.set(cache_key, response_data, timeout=60 * 15)

    return paginator.get_paginated_response(response_data)


@extend_schema(
    summary="Добавление/удаление номинаций у конкурса",
    description="Принимает список номинаций в формате JSON и добавляет или удаляет их у конкретного конкурса.",
    request=ContestChangeNominationSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "added": {"type": "array", "items": {"type": "integer"}},
                        "removed": {"type": "array", "items": {"type": "integer"}},
                    },
                },
            },
        },
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
        404: {"type": "object", "properties": {"message": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={"nomination_list": [{"id": 1, "name": "Лучший фильм"}]},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={
                "message": "Nominations updated successfully",
                "data": {"added": [1], "removed": []},
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Неверные данные",
            value={
                "error": "Invalid data",
                "errors": {"nomination_list": ["This field is required."]},
                "response_only": True,
            },
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    [IsAuthenticated, IsContestOwnerPermission, IsNotBlockUserPermission]
)
def add_or_remove_nomination_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    if not contest:
        return Response(
            data={"message": "contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = ContestChangeNominationSerializer(
        data=request.data, context={"contest": contest}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.update_nominations_in_contest()

    return Response(
        data={"message": "Nominations updated successfully", "data": data},
        status=status.HTTP_200_OK,
    )
