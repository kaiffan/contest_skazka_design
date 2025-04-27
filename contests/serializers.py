from rest_framework.serializers import ModelSerializer
from contests.models import Contest


class ContestSerializer(ModelSerializer[Contest]):
    class Meta:
        model = Contest
        fields = [
            "title",
            "description",
            "link_to_rules",
            "avatar",
            "date_start",
            "date_end",
            "organizer",
            "is_draft",
            "categories",
            "nomination",
            "criteria",
            "contest_stage",  # динамически подставлять стадию
            "jury",
        ]


class ContestAllSerializer(ModelSerializer[Contest]):
    class Meta:
        model = Contest
        fields = [
            "title",
            "avatar",
            "contest_categories",
            "contest_stage",  # динамически подставлять стадию энд дейт стейдж
        ]
