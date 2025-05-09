from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from authentication.permissions import IsAdminSystemPermission
from contests.models import Contest
from contests.serializers import (
    CreateBaseContestSerializer,
    UpdateBaseContestSerializer,
)
from participants.permissions import IsContestOwnerPermission


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
def create_contest_view(request: Request) -> Response:
    serializer = CreateBaseContestSerializer(
        data=request.data, context={"user_id": request.user.id}
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.create(validated_data=serializer.validated_data)

    return Response(status=status.HTTP_201_CREATED)


@api_view(http_method_names=["PATCH"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def update_contest_view(request: Request) -> Response:
    serializer = UpdateBaseContestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        contest = Contest.objects.get(id=request.contest_id)
    except Contest.DoesNotExist:
        return Response(
            data={"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer.update(instance=contest, validated_data=serializer.validated_data)

    return Response(status=status.HTTP_200_OK)


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsAdminSystemPermission])
def publish_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    contest.is_published = True
    contest.is_draft = False
    contest.save()

    return Response(
        data={"message": "Contest successfully published"}, status=status.HTTP_200_OK
    )


@api_view(http_method_names=["DELETE"])
@permission_classes(permission_classes=[IsAuthenticated, IsAdminSystemPermission])
def delete_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    contest.is_deleted = True
    contest.save()

    return Response(
        data={"message": "Contest successfully deleted"}, status=status.HTTP_200_OK
    )
