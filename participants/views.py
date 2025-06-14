from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from block_user.permissions import IsNotBlockUserPermission
from participants.permissions import IsContestOwnerPermission
from participants.serializers import (
    JuryParticipantSerializer,
    OrgCommitteeParticipantSerializer,
)


@extend_schema(
    summary="Обновление состава жюри конкурса",
    description="Изменяет список пользователей, назначенных в жюри конкурса.",
    request=JuryParticipantSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "added": {"type": "array", "items": {"type": "string"}},
                "removed": {"type": "array", "items": {"type": "string"}},
            },
        },
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса (жюри)",
            value={"jury_ids": [1, 2, 3]},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={
                "added": ["User 1 добавлен в жюри", "User 2 добавлен в жюри"],
                "removed": ["User 5 удалён из жюри"],
            },
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsNotBlockUserPermission,
    ]
)
def change_jury_view(request: Request) -> Response:
    serializer = JuryParticipantSerializer(
        data=request.data, context={"contest_id": request.contest_id}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data: dict[str, list[str]] = serializer.update_list_jury_in_contest()

    return Response(data=data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Обновление состава оргкомитета конкурса",
    description="Изменяет список пользователей, назначенных в оргкомитет конкурса.",
    request=OrgCommitteeParticipantSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "added": {"type": "array", "items": {"type": "string"}},
                "removed": {"type": "array", "items": {"type": "string"}},
            },
        },
        400: {
            "type": "object",
            "properties": {"error": {"type": "string"}, "errors": {"type": "object"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Пример запроса (оргкомитет)",
            value={"org_committee_ids": [1, 2, 3]},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={
                "added": [
                    "User 1 добавлен в оргкомитет",
                    "User 2 добавлен в оргкомитет",
                ],
                "removed": ["User 5 удалён из оргкомитета"],
            },
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsNotBlockUserPermission,
    ]
)
def change_or_committee_view(request: Request) -> Response:
    serializer = OrgCommitteeParticipantSerializer(
        data=request.data, context={"contest_id": request.contest_id}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data: dict[str, list[str]] = serializer.update_list_org_committee_in_contest()

    return Response(data=data, status=status.HTTP_200_OK)
