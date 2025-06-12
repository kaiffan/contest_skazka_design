from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from applications.enums import ApplicationStatus
from applications.filters import ApplicationFilter
from applications.models import Applications
from applications.paginator import ApplicationPaginator
from applications.serializers import (
    SendApplicationsSerializer,
    ApproveApplicationSerializer,
    RejectApplicationSerializer,
    ApplicationSerializer,
    ApplicationWithCriteriaSerializer,
    UpdateApplicationSerializer,
)
from block_user.permissions import IsNotBlockUserPermission
from contest_stage.permissions import CanSubmitApplicationPermission, CanCheckWorksPermission
from participants.permissions import (
    IsContestJuryPermission,
    IsOrgCommitteePermission,
    IsContestMemberPermission,
)


def get_filtered_applications(contest_id: str, status_filter: str):
    return Applications.objects.filter(
        contest_id=contest_id, status=status_filter
    ).all()


def get_applications_by_status(request: Request, status_filter: str) -> Response:
    paginator = ApplicationPaginator()
    queryset = get_filtered_applications(
        contest_id=request.contest_id, status_filter=status_filter
    )
    page = paginator.paginate_queryset(queryset=queryset, request=request)
    serializer = ApplicationSerializer(page, many=True)

    return paginator.get_paginated_response(data=serializer.data)


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsNotBlockUserPermission,
        CanSubmitApplicationPermission,
    ]
)
def send_applications_view(request: Request) -> Response:
    serializer = SendApplicationsSerializer(
        data=request.data, context={"user": request.user}
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(http_method_names=["PUT"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsNotBlockUserPermission,
        CanSubmitApplicationPermission
    ]
)
def approve_application_view(request: Request) -> Response:
    serializer = ApproveApplicationSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    approved_apps = serializer.save()

    return Response(
        data={
            "detail": f"{len(approved_apps)} заявок одобрено",
            "ids": [application.id for application in approved_apps],
        },
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["PATCH"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsNotBlockUserPermission,
        CanSubmitApplicationPermission
    ]
)
def reject_application_view(request: Request) -> Response:
    serializer = RejectApplicationSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(
        data={
            "message": "Application rejected",
        },
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_applications_view(request: Request) -> Response:
    return get_applications_by_status(
        request=request, status_filter=ApplicationStatus.pending.value
    )


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_applications_rejected_view(request: Request) -> Response:
    return get_applications_by_status(
        request=request, status_filter=ApplicationStatus.rejected.value
    )


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsOrgCommitteePermission,
        IsContestJuryPermission,
        IsNotBlockUserPermission,
    ]
)
def get_all_applications_approved_view(request: Request) -> Response:
    return get_applications_by_status(
        request=request, status_filter=ApplicationStatus.accepted.value
    )


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def get_application_view(request: Request) -> Response:
    application_id = request.data.get("application_id", None)

    if not application_id:
        return Response(
            data={"error": "Application id not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    application = Applications.objects.get(id=application_id)
    serializer = ApplicationWithCriteriaSerializer(instance=application)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsNotBlockUserPermission
    ]
)
def get_applications_user_view(request: Request) -> Response:
    user_applications = Applications.objects.filter(user_id=request.user.id, is_deleted=False).all()

    application_filter = ApplicationFilter(data=request.GET, queryset=user_applications)

    paginator = ApplicationPaginator()

    paginated_queryset = paginator.paginate_queryset(
        queryset=application_filter.qs, request=request
    )
    serializer = ApplicationSerializer(instance=paginated_queryset, many=True)

    return paginator.get_paginated_response(data=serializer.data)


@api_view(http_method_names=["PATCH"])
@permission_classes(
    [
        IsAuthenticated,
        IsNotBlockUserPermission,
        IsContestMemberPermission,
        CanSubmitApplicationPermission,
    ]
)
def update_application_view(request: Request) -> Response:
    application_id = request.data.get("application_id")

    if not application_id:
        return Response(
            data={"error": "Application id not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        application = Applications.objects.get(id=application_id)
    except Applications.DoesNotExist:
        return Response(
            data={"error": "Application not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = UpdateApplicationSerializer(
        instance=application, data=request.data, partial=True
    )

    if not serializer.is_valid(raise_exception=True):
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=["DELETE"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsNotBlockUserPermission
    ]
)
def delete_application_view(request: Request) -> Response:
    application_id = request.data.get("application_id")

    if not application_id:
        return Response(
            data={"error": "Application id not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        application = Applications.objects.get(id=application_id)
    except Applications.DoesNotExist:
        return Response(
            data={"error": "Application not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if application.user != request.user:
        return Response(data={"error": "You do not have permission to delete this application"},
                        status=status.HTTP_403_FORBIDDEN)

    application.is_deleted = True
    application.save(update_fields=["is_deleted"])

    return Response(
        data={"message": "Application successfully deleted"},
        status=status.HTTP_200_OK,
    )
