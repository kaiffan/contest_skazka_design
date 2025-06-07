from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest
from contests.serializers import FileConstraintChangeSerializer
from file_constraints.models import FileConstraint
from file_constraints.serailizers import FileConstraintSerializer
from participants.permissions import IsContestOwnerPermission


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def get_all_file_constraints_view(request: Request) -> Response:
    queryset = FileConstraint.objects.all()

    serializer = FileConstraintSerializer(instance=queryset, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def change_file_constraints_view(request: Request) -> Response:
    contest = get_object_or_404(Contest, id=request.contest_id)

    serializer = FileConstraintChangeSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(data={"message": serializer.errors}, status=status.HTTP_200_OK)

    serializer.update(instance=contest, validated_data=serializer.validated_data)

    return Response(data={"status": "success"}, status=status.HTTP_200_OK)
