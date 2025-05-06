from rest_framework.serializers import ModelSerializer

from criterias.models import Criteria


class CriteriaSerializer(ModelSerializer[Criteria]):
    class Meta:
        model = Criteria
        fields = ["id", "name", "description", "min_points", "max_points"]
        extra_kwargs = {
            "id": {"required": False},
            "name": {"required": True},
            "description": {"required": True},
            "min_points": {"required": True},
            "max_points": {"required": True},
        }
