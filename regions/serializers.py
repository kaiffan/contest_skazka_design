from rest_framework.serializers import ModelSerializer

from regions.models import Region


class RegionSerializer(ModelSerializer[Region]):
    class Meta:
        model = Region
        fields = "__all__"
