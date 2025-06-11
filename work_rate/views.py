from django.db.models import Sum, F, Value, Count
from django.db.models.functions import Concat
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from applications.models import Applications
from block_user.permissions import IsNotBlockUserPermission
from contest_stage.permissions import CanCheckWorksPermission
from contests.models import Contest
from contests.utils import get_current_contest_stage
from work_rate.utils import validate_count_criteria_by_contest

from participants.permissions import IsContestJuryPermission
from work_rate.models import WorkRate
from work_rate.serializers import (
    WorkRateSerializer,
    WorkRateContestAllSerializer,
    ApplicationRatesSerializer,
    RateSummarySerializer,
)


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
        CanCheckWorksPermission,
    ]
)
def work_rate_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    serializer = WorkRateSerializer(
        data=request.data,
        context={"contest": contest, "jury_id": request.user.id},
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
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
        CanCheckWorksPermission
    ]
)
def get_all_rated_works_in_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    work_rates = (
        WorkRate.objects.filter(application__contest_id=contest.id)
        .values("application_id")
        .annotate(total=Sum("rate"))
    )

    serializer = WorkRateContestAllSerializer(instance=work_rates, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
        CanCheckWorksPermission,
    ]
)
def get_all_rated_works_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    application_ids = (
        WorkRate.objects.filter(application__contest_id=contest.id)
        .values_list("application_id", flat=True)
        .distinct()
        .all()
    )

    application_queryset = Applications.objects.filter(id__in=application_ids).all()

    serializer = ApplicationRatesSerializer(instance=application_queryset, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["PATCH"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
        CanCheckWorksPermission
    ]
)
def update_rated_work_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    serializer = WorkRateSerializer(
        data=request.data, context={"jury_id": request.user.id, "contest": contest}
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.update(instance=None, validated_data=serializer.validated_data)
    return Response(
        data={"message": "Updated success"},
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
        CanCheckWorksPermission
    ]
)
def get_rated_work_by_jury_in_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    rates = (
        WorkRate.objects.filter(application__contest_id=contest.id)
        .select_related("jury__user")
        .annotate(
            full_name=Concat(
                F("jury__user__last_name"), Value(" "), F("jury__user__first_name")
            )
        )
        .values("jury_id", "full_name")
        .annotate(total_rates=Count("application_id", distinct=True))
    )

    serializer = RateSummarySerializer(rates, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
