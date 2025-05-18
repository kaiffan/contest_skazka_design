from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from regions.models import Region
from regions.serializers import RegionSerializer


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[])
def all_regions_view(request):
    contest_id = request.contest_id
    regions = Region.objects.all()

    if not contest_id:
        regions = regions.exclude(name="Онлайн")

    serializer = RegionSerializer(regions, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
