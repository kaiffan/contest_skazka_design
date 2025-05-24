from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request

from authentication.permissions import IsAdminSystemPermission
from contests.filter import ContestFilter
from contests.models import Contest
from contests.serializers import (
    CreateBaseContestSerializer,
    UpdateBaseContestSerializer,
    ContestByIdSerializer,
    ContestAllSerializer,
    ContestAllOwnerSerializer,
)
from participants.enums import ParticipantRole
from participants.permissions import IsContestOwnerPermission


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
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


@api_view(http_method_names=["PATCH"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def update_contest_view(request: Request) -> Response:
    serializer = UpdateBaseContestSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    contest = get_object_or_404(Contest, id=request.contest_id)

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


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def get_contest_by_id(request: Request) -> Response:
    instance = Contest.objects.prefetch_related(
        "criteria", "nominations", "age_category", "participants", "contest_stage"
    ).get(id=request.contest_id)

    serializer = ContestByIdSerializer(instance=instance)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_all_contests_not_permissions_view(request: Request) -> Response:
    contest_list = Contest.objects.filter(is_published=True, is_deleted=False).all()

    serializer = ContestAllSerializer(instance=contest_list, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def get_all_contests_view(request: Request) -> Response:
    contest_list = Contest.objects.filter(is_published=True, is_deleted=False).all()

    contest_filter = ContestFilter(data=request.GET, queryset=contest_list)
    filter_queryset = contest_filter.qs

    serializer = ContestAllSerializer(instance=filter_queryset, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def get_all_contests_owner_view(request: Request) -> Response:
    contests = Contest.objects.filter(
        participant__user=request.user,
        participant__role=ParticipantRole.owner.value,
    ).distinct()

    serializer = ContestAllOwnerSerializer(instance=contests, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)
