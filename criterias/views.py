from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from contests.serializers import ContestChangeCriteriaSerializer
from criterias.models import Criteria
from criterias.serializers import CriteriaSerializer
from participants.permissions import IsContestOwner


@api_view(http_method_names=["POST"])
@permission_classes([IsAuthenticated, IsContestOwner])
def change_criteria_contest_view(request: Request) -> Response:
    contest_id = request.headers.get("X-Contest-ID")

    if not contest_id:
        return Response(
            data={"message": "No Contest ID in header"},
            status=status.HTTP_404_NOT_FOUND,
        )

    contest = Contest.objects.get(id=contest_id)

    if not contest:
        return Response(
            data={"message": "contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = ContestChangeCriteriaSerializer(
        instance=contest, data=request.data, partial=False
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.update_criteria()

    return Response(
        data={"message": "Criteria updated successfully", "data": data},
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated, IsContestOwner])
def get_all_criteria_view(request: Request) -> Response:
    contest_id = request.headers.get("X-Contest-ID") # написать middleware для получения contest_id

    if not contest_id:
        return Response(
            data={"message": "No Contest ID in header"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        contest = Contest.objects.get(id=contest_id)
    except Contest.DoesNotExist:
        return Response(
            data={"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    selected_criteria_ids = set(
        contest.criteria.values_list("id", flat=True)
    )

    available_criteria = Criteria.objects.exclude(id__in=selected_criteria_ids)

    serializer = CriteriaSerializer(available_criteria, many=True)

    return Response(
        data={
            "data": serializer.data,
        }, status=status.HTTP_200_OK
    )

