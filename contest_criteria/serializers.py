from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from contest_criteria.models import ContestCriteria
from criteria.models import Criteria


class ContestCriteriaSerializer(ModelSerializer[ContestCriteria]):
    criteria_name = SerializerMethodField()

    class Meta:
        model = ContestCriteria
        fields = [
            "criteria_name",
            "description",
            "min_points",
            "max_points",
        ]

    def get_criteria_name(self, instance):
        return Criteria.objects.get(id=instance.criteria_id).name


class ContestCriteriaFullSerializer(ModelSerializer[ContestCriteria]):
    criteria_name = SerializerMethodField()
    criteria_id = SerializerMethodField()

    class Meta:
        model = ContestCriteria
        fields = [
            "criteria_id",
            "criteria_name",
            "description",
            "min_points",
            "max_points",
        ]

    def get_criteria_name(self, instance):
        return Criteria.objects.get(id=instance.criteria_id).name

    def get_criteria_id(self, instance):
        return Criteria.objects.get(id=instance.criteria_id).id
