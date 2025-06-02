from rest_framework.serializers import ModelSerializer
from nomination.models import Nominations


class NominationsSerializer(ModelSerializer[Nominations]):
    class Meta:
        model = Nominations
        fields = ["name"]


class FullNominationsSerializer(ModelSerializer[Nominations]):
    class Meta:
        model = Nominations
        fields = "__all__"
