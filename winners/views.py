from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from contests_contest_stage.models import ContestsContestStage
from participants.permissions import IsContestOwnerPermission
from winners.serializers import ContestWinnersSerializer


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def get_contest_winners(request: Request) -> Response:
    contest: Contest = get_object_or_404(Contest, id=request.contest_id)
    current_contest_stage: bool = ContestsContestStage.objects.filter(
        contest_id=contest.id,
        stage__name="Подведение итогов"
    ).exists()

    if not current_contest_stage:
        return Response(data={"error": "Не подходящая стадия для подведения итогов конкурса"})

    serializer = ContestWinnersSerializer(instance=contest)
    return Response(data=serializer.data, status=status.HTTP_200_OK)