from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from applications.enums import ApplicationStatus
from applications.models import Applications
from applications.paginator import ApplicationPaginator
from applications.serializers import (
    SendApplicationsSerializer,
    ApproveApplicationSerializer,
    RejectApplicationSerializer,
    ApplicationSerializer,
)
from participants.permissions import IsContestJury


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
def send_applications_view(request: Request) -> Response:
    serializer = SendApplicationsSerializer(
        data=request.data, context={"user_id": request.user.id}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(http_method_names=["PUT"])
@permission_classes(permission_classes=[IsAuthenticated])
def approve_application_view(request: Request) -> Response:
    serializer = ApproveApplicationSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    application = Applications.objects.get(id=serializer.validated_data["id"])
    serializer.update(instance=application, validated_data={})

    return Response(
        data={
            "message": "Application approved",
        },
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["PATCH"])
@permission_classes(permission_classes=[IsAuthenticated])
def reject_application_view(request: Request) -> Response:
    serializer = RejectApplicationSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    application = Applications.objects.get(id=serializer.validated_data["id"])
    serializer.update(instance=application, validated_data=serializer.validated_data)

    return Response(
        data={
            "message": "Application rejected",
        },
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestJury])
def get_all_applications_view(request: Request) -> Response:
    contest_id = request.headers.get("X-Contest-ID", None)

    if not contest_id:
        return Response(
            data={"message": "No Contest ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    paginator = ApplicationPaginator()

    applications_contest = Applications.objects.filter(
        contest_id=contest_id, status=ApplicationStatus.accepted.value
    ).all()

    page = paginator.paginate_queryset(applications_contest, request)

    serializer = ApplicationSerializer(page, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def get_application_view(request: Request) -> Response:
    pass
