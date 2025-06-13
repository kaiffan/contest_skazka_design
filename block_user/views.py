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


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsAdminSystemPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_users_view(request: Request) -> Response:
    blocked_user_ids = UserBlock.objects.filter(is_blocked=True).values_list("user_id", flat=True)
    user_list = Users.objects.all().exclude(id=request.user.id).exclude(id__in=blocked_user_ids)

    paginator = BlockUserPagination()
    users_page = paginator.paginate_queryset(queryset=user_list, request=request)

    serializer = UserParticipantSerializer(instance=users_page, many=True)
    return paginator.get_paginated_response(data=serializer.data)

