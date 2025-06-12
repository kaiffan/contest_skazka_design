from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from block_user.permissions import IsNotBlockUserPermission
from contest_stage.models import ContestStage
from contest_stage.serializers import ContestStageSerializer
from contests.models import Contest
from contests.serializers import ContestChangeStageSerializer


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def all_contest_stage_view(request):
    all_contest_stages = ContestStage.objects.all()
    serializer = ContestStageSerializer(all_contest_stages, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["POST"])
@permission_classes([IsAuthenticated, IsNotBlockUserPermission])
def add_or_remove_contest_stage_in_contest_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    if not contest:
        return Response(
            data={"message": "contest not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = ContestChangeStageSerializer(
        data=request.data, context={"contest": contest}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.change_contest_stages_in_contest()

    return Response(
        data={"message": "Contest stage updated successfully", "data": data},
        status=status.HTTP_200_OK,
    )
