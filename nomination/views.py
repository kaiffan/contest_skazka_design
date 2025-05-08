from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from nomination.models import Nominations
from nomination.pagginator import NominationsPaginator
from nomination.serializers import NominationsSerializer
from participants.permissions import IsContestOwnerPermission


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsContestOwnerPermission])
def get_nominations(request: Request) -> Response:
    paginator = NominationsPaginator()
    queryset = Nominations.objects.all()

    page = paginator.paginate_queryset(queryset=queryset, request=request)

    serializer = NominationsSerializer(page, many=True)

    return paginator.get_paginated_response(data=serializer.data)
