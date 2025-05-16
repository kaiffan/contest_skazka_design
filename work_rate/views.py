from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from work_rate.utils import validate_count_criteria_by_contest

from participants.permissions import IsContestJuryPermission
from work_rate.models import WorkRate
from work_rate.serializers import WorkRateSerializer, WorkRateAllSerializer


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])  # , IsContestJuryPermission
def work_rate_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    serializer = WorkRateSerializer(
        data=request.data, many=True, context={"contest": contest}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    work_rate_list = serializer.create(validated_data=serializer.validated_data)

    application = work_rate_list[0].application

    valid_rate: bool = validate_count_criteria_by_contest(
        contest=contest, application=application
    )

    if not valid_rate:
        return Response(
            data={
                "message": "Invalid rate for contest",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])  # , IsContestJuryPermission
def get_all_rated_works_in_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    work_rates = (
        WorkRate.objects.filter(application__contest_id=contest.id)
        .values("application_id")
        .annotate(total=Sum("rate"))
    )

    serializer = WorkRateAllSerializer(work_rates, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["PATCH"])
@permission_classes(permission_classes=[IsAuthenticated])  # , IsContestJuryPermission
def update_rated_work_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    for _, element in enumerate(request.data):
        application_id = element.get("application_id")
        criteria_id = element.get("criteria_id")

        try:
            work_rate = WorkRate.objects.get(
                application_id=application_id,
                criteria_id=criteria_id,
                application__contest=contest,
            )
        except WorkRate.DoesNotExist:
            return Response(
                data={"message": "Work rate not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WorkRateSerializer(
            instance=work_rate, data=element, partial=True, context={"contest": contest}
        )
        if not serializer.is_valid(raise_exception=True):
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.update(instance=work_rate, validated_data=serializer.validated_data)

    return Response(data="Update successfuly", status=status.HTTP_200_OK)
