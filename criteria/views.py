from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from contests.serializers import ContestChangeCriteriaSerializer
from criteria.models import Criteria
from criteria.serializers import CriteriaSerializer, CriteriaNotRequiredSerializer
from participants.permissions import IsContestOwnerPermission


@api_view(http_method_names=["POST"])
@permission_classes([IsAuthenticated, IsContestOwnerPermission])
def add_or_remove_criteria_contest_view(request: Request) -> Response:
    contest = Contest.objects.get(id=request.contest_id)

    if not contest:
        return Response(
            data={"message": "contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = ContestChangeCriteriaSerializer(
        data=request.data, context={"contest": contest}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.update_criteria()

    return Response(
        data={"message": "Criteria updated successfully", "data": data},
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated, IsContestOwnerPermission])
def get_all_criteria_view(request: Request) -> Response:
    try:
        contest = Contest.objects.get(id=request.contest_id)
    except Contest.DoesNotExist:
        return Response(
            data={"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    selected_criteria_ids = set(contest.criteria.values_list("id", flat=True))

    available_criteria = Criteria.objects.exclude(id__in=selected_criteria_ids)

    serializer = CriteriaSerializer(available_criteria, many=True)

    return Response(
        data={
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["PATCH"])
@permission_classes([IsAuthenticated, IsContestOwnerPermission])
def update_criteria_view(request: Request) -> Response:
    criteria_id = request.data["id"]

    if not criteria_id:
        return Response(
            data={"error": "criteria_id not found"}, status=status.HTTP_404_NOT_FOUND
        )

    instance = get_object_or_404(Criteria, id=criteria_id)

    serializer = CriteriaNotRequiredSerializer(
        instance=instance, data=request.data, partial=True
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(data=serializer.data, status=status.HTTP_200_OK)
