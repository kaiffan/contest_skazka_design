from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from contest_categories.models import ContestCategories
from contests.models import Contest
from regions.models import Region


class ContestByIdSerializer(ModelSerializer[Contest]):
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


class BaseContestSerializer(ModelSerializer[Contest]):
    contest_categories_name = CharField(write_only=True)

    class Meta:
        model = Contest
        fields = [
            "title",
            "description",
            "avatar",
            "link_to_rules",
            "organizer",
            "region_id",
            "contest_categories_name",
        ]
        extra_kwargs = {
            "title": {"required": True},
            "description": {"required": True},
            "link_to_rules": {"required": True},
            "avatar": {"required": True},
            "region_id": {"required": True},
            "contest_categories_name": {"required": True},
            "organizer": {"required": True},
        }

    def create(self, validated_data):
        name_contest_categories: str = validated_data.pop(
            "contest_categories_name", None
        )

        contest_category, _ = ContestCategories.objects.get_or_create(
            name=name_contest_categories
        )

        Contest.objects.create(
            contest_categories_id=contest_category.id, **validated_data
        )

    def update(self, instance, validated_data):
        category_name = validated_data.pop("contest_categories_name", None)
        if category_name:
            contest_category, _ = ContestCategories.objects.get_or_create(
                name=category_name
            )
            instance.contest_categories_id = contest_category.id

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate_region_id(self, region_id: int):
        if not Region.objects.filter(id=region_id).exists():
            raise ValidationError("Region does not exist")
        return region_id
