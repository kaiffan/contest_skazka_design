from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from block_user.permissions import IsNotBlockUserPermission
from contests.models import Contest
from contests.serializers import FileConstraintChangeSerializer
from file_constraints.models import FileConstraint
from file_constraints.serailizers import FileConstraintSerializer
from participants.permissions import IsContestOwnerPermission


@extend_schema(
    summary="Получение всех ограничений на файлы",
    description="Возвращает список всех доступных ограничений на загрузку файлов.",
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_all_file_constraints_view(request: Request) -> Response:
    queryset = FileConstraint.objects.all()

    serializer = FileConstraintSerializer(instance=queryset, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Добавление/удаление ограничений на файлы у конкурса",
    description="Принимает список ID ограничений и обновляет их у конкретного конкурса.",
    request=FileConstraintChangeSerializer,
    responses={
        200: {"type": "object", "properties": {"status": {"type": "string"}}},
        400: {"type": "object", "properties": {"message": {"type": "object"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример запроса",
            value={"file_constraint_ids": [1, 2, 3]},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ", value={"status": "success"}, response_only=True
        ),
        OpenApiExample(
            name="Ошибка: Неверные данные",
            value={"message": {"file_constraint_ids": ["This field is required."]}},
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
def change_file_constraints_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    serializer = FileConstraintChangeSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(data={"message": serializer.errors}, status=status.HTTP_200_OK)

    serializer.update(instance=contest, validated_data=serializer.validated_data)

    return Response(data={"status": "success"}, status=status.HTTP_200_OK)
