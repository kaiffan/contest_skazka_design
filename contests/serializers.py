from typing import List, Set, Dict, Any

from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField, ListField, JSONField
from rest_framework.serializers import ModelSerializer, Serializer

from contest_categories.models import ContestCategories
from contests.models import Contest
from criteria.models import Criteria
from criteria.serializers import CriteriaSerializer
from participants.enums import ParticipantRole
from participants.models import Participant
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
    region_id = IntegerField()

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

    def create(self, validated_data):
        name_contest_categories: str = validated_data.pop(
            "contest_categories_name", None
        )

        contest_category, _ = ContestCategories.objects.get_or_create(
            name=name_contest_categories
        )

        validated_data["contest_categories_id"] = contest_category.id

        contest = Contest.objects.create(
            **validated_data
        )

        user_id = self.context.get("user_id")

        Participant.objects.create(
            contest_id=contest.id,
            user_id=user_id,
            role=ParticipantRole.owner.value
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


class ContestChangeCriteriaSerializer(Serializer):
    criteria_list = ListField(
        child=JSONField(),
        required=True
    )

    def validate_criteria_list(self, data):
        if not data:
            raise ValidationError("criteria_list cannot be empty")
        return data

    def update_criteria(self):
        contest = self.context.get("contest", None)
        criteria_list = self.validated_data.get("criteria_list")
        print(criteria_list)
        existing_criteria: List[int] = [
            criteria.get("id")
            for criteria in criteria_list
            if criteria.get("id") is not None
        ]
        print(existing_criteria)

        new_criteria_list: List[Criteria] = [
            Criteria(
                name=criteria.get("name"),
                description=criteria.get("description"),
                min_points=criteria.get("min_points"),
                max_points=criteria.get("max_points"),
            )
            for criteria in criteria_list
            if criteria.get("id") is None
        ]

        new_criteria_name: List[str] = [criteria.name for criteria in new_criteria_list]

        with transaction.atomic():
            existing_name_criteria = set(
                Criteria.objects.filter(name__in=new_criteria_name).values_list(
                    "name", flat=True
                )
            )

            only_new_criteria: List[Criteria] = [
                criteria
                for criteria in new_criteria_list
                if criteria.name not in existing_name_criteria
            ]

            exists_criteria_in_db: Set[int] = set(
                contest.criteria.values_list("id", flat=True)
            )
            print(exists_criteria_in_db)

            criteria_to_remove: Set[int] = exists_criteria_in_db - set(
                existing_criteria
            )
            criteria_to_add: Set[int] = set(existing_criteria) - exists_criteria_in_db
            print(criteria_to_add)

            if criteria_to_remove:
                contest.criteria.remove(*criteria_to_remove)

            if criteria_to_add:
                contest.criteria.add(*criteria_to_add)

            created_criteria_list: List[Criteria] = Criteria.objects.bulk_create(
                objs=only_new_criteria
            )
            if created_criteria_list:
                contest.criteria.add(*created_criteria_list)

            return None
