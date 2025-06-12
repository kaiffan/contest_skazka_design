from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contest_stage.permissions import CanFinalizeResultsPermission
from contests.models import Contest
from participants.permissions import IsContestOwnerPermission
from winners.serializers import ContestWinnersSerializer


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission, CanFinalizeResultsPermission])
def get_contest_winners(request: Request) -> Response:
    contest: Contest = get_object_or_404(Contest, id=request.contest_id)

    serializer = ContestWinnersSerializer(instance=contest)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
