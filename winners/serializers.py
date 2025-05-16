from django.db.models import F, Sum
from rest_framework.fields import SerializerMethodField, CharField
from rest_framework.serializers import ModelSerializer, Serializer

from applications.models import Applications
from contests.models import Contest
from winners.models import Winners


class ApplicationRatedSerializer(ModelSerializer):
    sum_rate = SerializerMethodField()
    place = SerializerMethodField()

    class Meta:
        model = Applications
        fields = ("id", "name", "annotation", "user", "sum_rate", "place")

    def get_sum_rate(self, application):
        contest = self.context.get("contest")
        sum_rate = Winners.objects.filter(application_id=application.id, contest_id=contest.id).first()
        return sum_rate.sum_rate


    def get_place(self, application):
        contest = self.context.get("contest")
        sum_rate = Winners.objects.filter(application_id=application.id, contest_id=contest.id).first()
        return sum_rate.place


class AgeCategoryWinnersSerializer(Serializer):
    age_category = CharField()
    winners = ApplicationRatedSerializer(many=True)

    def to_representation(self, instance):
        sorted_winners = sorted(
            instance["winners"], key=lambda x: int(x.get("place", 0)), reverse=True
        )

        return {"age_category": instance["age_category"], "winners": sorted_winners}


class NominationWinnersSerializer(Serializer):
    nomination = CharField()
    age_categories = AgeCategoryWinnersSerializer(many=True)


class ContestWinnersSerializer(ModelSerializer[Contest]):
    nominations = NominationWinnersSerializer(many=True, source="nominations")

    class Meta:
        model = Contest
        fields = ("id", "title", "nominations")
