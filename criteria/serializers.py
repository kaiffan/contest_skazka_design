from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from criteria.models import Criteria


class CriteriaSerializer(ModelSerializer[Criteria]):
    class Meta:
        model = Criteria
        fields = "__all__"
