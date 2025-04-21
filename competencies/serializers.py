from rest_framework.serializers import ModelSerializer

from competencies.models import Competencies


class CompetenciesSerializer(ModelSerializer):
    class Meta:
        model = Competencies
        fields = "__all__"
