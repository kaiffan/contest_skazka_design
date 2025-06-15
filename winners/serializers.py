from collections import defaultdict

from rest_framework.fields import SerializerMethodField, CharField
from rest_framework.serializers import ModelSerializer, Serializer

from applications.models import Applications
from contests.models import Contest
from winners.models import Winners


class ApplicationRatedSerializer(ModelSerializer[Applications]):
    sum_rate = SerializerMethodField()
    place = SerializerMethodField()
    user_fio = SerializerMethodField()
    user_email = SerializerMethodField()

    class Meta:
        model = Applications
        fields = (
            "id",
            "name",
            "annotation",
            "user_fio",
            "sum_rate",
            "place",
            "user_email",
        )

    def get_winner_qs(self, application):
        contest = self.context.get("contest")
        return (
            Winners.objects.filter(application_id=application.id, contest_id=contest.id)
            .only("sum_rate", "place")
            .first()
        )

    def get_user_fio(self, application: Applications):
        return application.user.get_fio()

    def get_user_email(self, application: Applications):
        return application.user.email

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
        data = super().to_representation(instance)
        data["winners"].sort(key=lambda x: int(x.get("place", 0)))
        return data


class NominationWinnersSerializer(Serializer):
    nomination = CharField(source="name")
    age_categories = SerializerMethodField()

    def get_age_categories(self, obj):
        contest = self.context.get("contest")

        winners = Winners.objects.filter(
            contest=contest, application__nomination=obj
        ).select_related("application")

        grouped = defaultdict(list)
        for winner in winners:
            grouped[winner.application.age_category].append(winner.application)

        result = []
        for age_name, apps in grouped.items():
            serialized_data = {
                "age_category": age_name,
                "winners": ApplicationRatedSerializer(
                    apps, many=True, context=self.context
                ).data,
            }
            result.append(serialized_data)

        return result


class ContestWinnersSerializer(ModelSerializer[Contest]):
    nominations = NominationWinnersSerializer(many=True)

    class Meta:
        model = Contest
        fields = ("id", "title", "nominations")
