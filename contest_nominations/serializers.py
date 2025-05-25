from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from contest_nominations.models import ContestNominations
from nomination.models import Nominations


class ContestNominationsSerializer(ModelSerializer[ContestNominations]):
    nomination_name = SerializerMethodField()

    class Meta:
        model = ContestNominations
        fields = [
            "nomination_name",
            "description",
        ]

    def get_nomination_name(self, instance):
        return Nominations.objects.get(id=instance.nomination_id).name
