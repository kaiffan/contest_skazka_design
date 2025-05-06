from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from criteria.models import Criteria


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

    def validate(self, attrs):
        min_points = attrs.get("min_points")
        max_points = attrs.get("max_points")

        if min_points >= max_points:
            raise ValidationError(
                {
                    "min_points": "Значение 'min_points' должно быть меньше, чем 'max_points'."
                }
            )

        return attrs


class CriteriaNotRequiredSerializer(ModelSerializer[Criteria]):
    class Meta:
        model = Criteria
        fields = ["id", "name", "description", "min_points", "max_points"]
        extra_kwargs = {
            "id": {"required": True},
            "name": {"required": False},
            "description": {"required": False},
            "min_points": {"required": False},
            "max_points": {"required": False},
        }

    def validate(self, attrs):
        db_min_points: int = self.instance.min_points
        db_max_points: int = self.instance.max_points

        new_min: int = attrs.get("min_points", db_min_points)
        new_max: int = attrs.get("max_points", db_max_points)

        if new_min >= new_max:
            raise ValidationError(
                {
                    "min_points": "Значение 'min_points' должно быть меньше, чем 'max_points'."
                }
            )

        return attrs
