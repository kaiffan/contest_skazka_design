from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from contests.models import Contest
from contests.serializers import BaseContestSerializer
from participants.permissions import IsContestOwner


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
def create_contest_view(request: Request) -> Response:
    serializer = BaseContestSerializer(data=request.data, context={"user_id": request.user.id})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.create(validated_data=serializer.validated_data)

    return Response(status=status.HTTP_201_CREATED)

@api_view(http_method_names=["PUT"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwner])
def update_contest_view(request: Request) -> Response:
    serializer = BaseContestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        contest = Contest.objects.get(id=request.contest_id)
    except Contest.DoesNotExist:
        return Response(
            data={"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer.update(instance=contest, validated_data=serializer.validated_data)

    return Response(status=status.HTTP_200_OK)
