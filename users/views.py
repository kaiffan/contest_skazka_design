from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models import Users
from participants.permissions import IsContestOwnerPermission

from users.serializers import (
    ContestDataUpdateSerializer,
    UserDataPatchSerializer,
    UserFullDataSerializer,
    AllUsersShortDataSerializer,
)


@api_view(http_method_names=["PUT"])
@permission_classes(permission_classes=[IsAuthenticated])
def contest_data_update_view(request) -> Response:
    serializer = ContestDataUpdateSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.update_user_data(user=request.user)

    return Response(
        data={"message": "Данные успешно обновлены", "data": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["PATCH"])
@permission_classes(permission_classes=[IsAuthenticated])
def user_data_update_view(request) -> Response:
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


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def user_data_get_view(request) -> Response:
    serializer = UserFullDataSerializer(request.user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def all_users_view(request) -> Response:
    email: str = request.query_params.get("filter", None)

    queryset = Users.objects.all()

    if email:
        queryset = queryset.filter(email=email)

    serializer = AllUsersShortDataSerializer(data=queryset, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)
