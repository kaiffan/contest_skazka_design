from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from participants.serializers import JuryParticipantSerializer


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
def change_jury_view(request: Request) -> Response:
    contest_id = request.headers.get("X-Contest-ID")

    serializer = JuryParticipantSerializer(
        data=request.data, context={"contest_id": contest_id}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data: dict[str, list[str]] = serializer.update_list_jury_in_contest()

    return Response(data=data, status=status.HTTP_200_OK)
