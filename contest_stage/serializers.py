from contest_stage.models import ContestStage
from rest_framework.serializers import ModelSerializer


class ContestStageSerializer(ModelSerializer[ContestStage]):
    class Meta:
        model = ContestStage
        fields = "__all__"
