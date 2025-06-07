from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from authentication.permissions import IsAdminSystemPermission
from block_user.models import UserBlock
from block_user.paginator import BlockUserPagination
from block_user.serializers import (
    BlockUserSerializer,
    UnblockUserSerializer,
    AllBlockUsersSerializer,
)


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsAdminSystemPermission])
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


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsAdminSystemPermission])
def unblock_user_view(request: Request) -> Response:
    serializer = UnblockUserSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(
        data={"success": "Пользователь успешно разблокирован"},
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsAdminSystemPermission])
def get_all_blocked_users_view(request: Request) -> Response:
    queryset = (
        UserBlock.objects.prefetch_related("user", "blocked_by")
        .filter(is_blocked=True)
        .all()
    )

    paginator = BlockUserPagination()
    result_page = paginator.paginate_queryset(queryset=queryset, request=request)

    serializer = AllBlockUsersSerializer(result_page, many=True)
    return paginator.get_paginated_response(data=serializer.data)
