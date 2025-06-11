from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from authentication.models import Users
from block_user.permissions import IsNotBlockUserPermission
from participants.permissions import IsContestOwnerPermission

from users.serializers import (
    ContestDataUpdateSerializer,
    UserDataPatchSerializer,
    UserFullDataSerializer,
    UserShortDataSerializer,
    UserCompetenciesSerializer,
    UserParticipantSerializer,
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


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def user_data_get_view(request: Request) -> Response:
    serializer = UserFullDataSerializer(request.user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def user_short_data_get_view(request: Request) -> Response:
    serializer = UserShortDataSerializer(instance=request.user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
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


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def user_competencies_jury_view(request: Request) -> Response:
    email = request.data.get("email", None)

    if not email:
        return Response(data={"error": "Not exists email"})

    user = Users.objects.get(email=email)
    serializer = UserCompetenciesSerializer(instance=user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
