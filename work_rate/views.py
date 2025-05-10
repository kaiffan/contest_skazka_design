from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from utils import validate_count_criteria_by_contest

from participants.permissions import IsContestJuryPermission
from work_rate.models import WorkRate
from work_rate.serializers import WorkRateSerializer, WorkRateAllSerializer


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestJuryPermission])
def work_rate_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    serializer = WorkRateSerializer(data=request.data, many=True)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    work_rate_list = WorkRate.objects.bulk_create(
        [WorkRate(**validated_data) for validated_data in serializer.validated_data]
    )

    application = work_rate_list[0].application

    validate_count_criteria_by_contest(
        contest=contest,
        application=application
    )

    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestJuryPermission])
def get_all_rated_works_view(request: Request) -> Response:
    work_rate_list = WorkRate.objects.all()
    serializer = WorkRateAllSerializer(work_rate_list, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)
