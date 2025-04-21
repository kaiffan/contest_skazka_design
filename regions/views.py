from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from regions.models import Region
from regions.serializers import RegionSerializer


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def all_regions_view(request):
    regions = Region.objects.all()
    serializer = RegionSerializer(regions, many=True)

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(data=serializer.data, status=status.HTTP_200_OK)
