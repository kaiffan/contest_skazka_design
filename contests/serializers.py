from typing import List, Set, Dict, Any

from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from contest_categories.models import ContestCategories
from contests.models import Contest
from criterias.models import Criteria
from criterias.serializers import CriteriaSerializer
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


class ContestChangeCriteriaSerializer(ModelSerializer[Contest]):
    criteria_list = CriteriaSerializer(many=True, source="criteria")

    class Meta:
        model = Contest
        fields = ["criteria_list"]
        extra_kwargs = {"criteria_list": {"required": True}}

    def validate_criteria_list(self, data):
        if not data:
            raise ValidationError("criteria_list cannot be empty")
        return data

    def update_criteria(self) -> Dict[str, Any]:
        criteria_list = self.validated_data["criteria_list"]
        existing_criteria: List[int] = [
            criteria.get("id")
            for criteria in criteria_list
            if criteria.get("id") is not None
        ]

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
                self.instance.criteria.values_list("id", flat=True)
            )

            criteria_to_remove: Set[int] = exists_criteria_in_db - set(
                existing_criteria
            )
            criteria_to_add: Set[int] = set(existing_criteria) - exists_criteria_in_db

            if criteria_to_remove:
                self.instance.criteria.remove(*criteria_to_remove)

            if criteria_to_add:
                self.instance.criteria.add(*criteria_to_add)

            created_criteria_list: List[Criteria] = Criteria.objects.bulk_create(
                objs=only_new_criteria
            )
            if created_criteria_list:
                self.instance.criteria.add(*created_criteria_list)

            return {
                "created_criteria": created_criteria_list,
                "remove_criteria": list(criteria_to_remove),
                "add_criteria": list(criteria_to_add),
            }
