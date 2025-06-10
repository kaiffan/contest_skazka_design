from rest_framework.fields import SerializerMethodField, CharField
from rest_framework.serializers import ModelSerializer, Serializer

from applications.models import Applications
from contests.models import Contest
from winners.models import Winners


class ApplicationRatedSerializer(ModelSerializer):
    sum_rate = SerializerMethodField()
    place = SerializerMethodField()
    user_fio = SerializerMethodField()

    class Meta:
        model = Applications
        fields = ("id", "name", "annotation", "user_fio", "sum_rate", "place")

    def get_winner_qs(self, application):
        contest = self.context.get("contest")
        return (
            Winners.objects.filter(application_id=application.id, contest_id=contest.id)
            .only("sum_rate", "place")
            .first()
        )

    def get_user_fio(self, application: Applications):
        user = application.user
        return f"{user.first_name} {user.last_name}"

    def get_sum_rate(self, application):
        winner = self.get_winner_qs(application)
        return winner.sum_rate if winner else None

    def get_place(self, application):
        winner = self.get_winner_qs(application)
        return winner.place if winner else None


class AgeCategoryWinnersSerializer(Serializer):
    age_category = CharField()
    winners = ApplicationRatedSerializer(many=True)

    def to_representation(self, instance):
        sorted_winners = sorted(
            instance["winners"], key=lambda x: int(x.get("place", 0))
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
