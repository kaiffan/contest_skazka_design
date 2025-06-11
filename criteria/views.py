from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from block_user.permissions import IsNotBlockUserPermission
from contest_criteria.models import ContestCriteria
from contest_criteria.serializers import ContestCriteriaFullSerializer
from contests.models import Contest
from contests.serializers import ContestChangeCriteriaSerializer
from criteria.models import Criteria
from criteria.pagginator import CriteriaPaginator
from criteria.serializers import CriteriaSerializer
from participants.permissions import IsContestOwnerPermission
from django.core.cache import cache


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsNotBlockUserPermission,
    ]
)
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

    data = serializer.update_criteria_in_contest()

    return Response(
        data={"message": "Criteria updated successfully", "data": data},
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_criteria_view(request: Request) -> Response:
    cache_key = f"criteria_all_{request.query_params.get('search', 'all')}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(data=cached_data, status=status.HTTP_200_OK)

    queryset = Criteria.objects.only("name").all()
    search = request.query_params.get("search", None)

    if search:
        queryset = queryset.filter(name__icontains=search)

    paginator = CriteriaPaginator()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    serializer = CriteriaSerializer(instance=paginated_queryset, many=True)

    response_data = {
        "data": serializer.data,
        "message": f"All names by {search}" if search else "All nominations",
    }

    cache.set(cache_key, response_data, timeout=60 * 15)

    return paginator.get_paginated_response(response_data)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_criteria_by_contest_view(request: Request) -> Response:
    criteria_by_contest = ContestCriteria.objects.filter(
        contest_id=request.contest_id
    ).all()

    serializer = ContestCriteriaFullSerializer(instance=criteria_by_contest, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
