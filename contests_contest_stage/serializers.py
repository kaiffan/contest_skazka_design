from rest_framework.serializers import ModelSerializer

from contest_stage.serializers import ContestStageSerializer
from contests_contest_stage.models import ContestsContestStage


class ContestsContestStageSerializer(ModelSerializer[ContestsContestStage]):
    stage = ContestStageSerializer()

    class Meta:
        model = ContestsContestStage
        fields = [
            "stage",
            "start_date",
            "end_date",
        ]