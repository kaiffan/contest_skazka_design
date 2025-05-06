from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from participants.permissions import IsContestOwnerPermission
from participants.serializers import (
    JuryParticipantSerializer,
    OrgCommitteeParticipantSerializer,
)


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def change_jury_view(request: Request) -> Response:
    serializer = JuryParticipantSerializer(
        data=request.data, context={"contest_id": request.contest_id}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data: dict[str, list[str]] = serializer.update_list_jury_in_contest()

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def change_or_committee_view(request: Request) -> Response:
    serializer = OrgCommitteeParticipantSerializer(
        data=request.data, context={"contest_id": request.contest_id}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data: dict[str, list[str]] = serializer.update_list_org_committee_in_contest()

    return Response(data=data, status=status.HTTP_200_OK)
