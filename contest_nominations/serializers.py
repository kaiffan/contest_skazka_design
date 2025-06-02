from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from contest_nominations.models import ContestNominations
from nomination.models import Nominations


class ContestNominationsSerializer(ModelSerializer[ContestNominations]):
    nomination_name = SerializerMethodField()
    nomination_id = SerializerMethodField()

    class Meta:
        model = ContestNominations
        fields = [
            "nomination_id",
            "nomination_name",
            "description",
        ]

    def get_nomination_name(self, instance):
        return Nominations.objects.get(id=instance.nomination_id).name

    def get_nomination_id(self, instance):
        return Nominations.objects.get(id=instance.nomination_id).id
