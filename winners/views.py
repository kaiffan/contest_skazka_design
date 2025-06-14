from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contest_stage.permissions import CanFinalizeResultsPermission
from contests.models import Contest
from contests.serializers import ContestWinnerSerializer
from participants.permissions import IsContestOwnerPermission
from winners.serializers import ContestWinnersSerializer


@api_view(http_method_names=['GET'])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission, CanFinalizeResultsPermission])
def get_contest_winners_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    winner_serializer = ContestWinnerSerializer(context={'contest': contest})
    winner_serializer.change_winners_by_contest()

    output_serializer = ContestWinnersSerializer(instance=contest)
    return Response(data=output_serializer.data, status=status.HTTP_200_OK)
