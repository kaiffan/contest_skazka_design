from typing import List, Set, Dict, Any, NoReturn

from django.db import transaction
from django.db.models import Model
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField, ListField, JSONField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from age_categories.models import AgeCategories
from contest_categories.models import ContestCategories
from contests.models import Contest
from criteria.models import Criteria
from nomination.models import Nominations
from participants.enums import ParticipantRole
from participants.models import Participant
from regions.models import Region


class ContestByIdSerializer(ModelSerializer[Contest]):
    jury = SerializerMethodField()
    criteria = SerializerMethodField()
    categories = SerializerMethodField()
    nomination = SerializerMethodField()
    age_categories = SerializerMethodField()


    class Meta:
        model = Contest
        fields = [
            "title",
            "description",
            "link_to_rules",
            "avatar",
            "organizer",
            "is_draft",
            "categories",
            "nomination",
            "criteria",
            "age_categories",
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


class CreateBaseContestSerializer(ModelSerializer[Contest]):
    contest_categories_name = CharField(write_only=True)
    age_category = ListField(child=IntegerField(), write_only=True)
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
            "age_category",
        ]
        extra_kwargs = {
            "title": {"required": True},
            "description": {"required": True},
            "avatar": {"required": True},
            "link_to_rules": {"required": True},
            "organizer": {"required": True},
            "region_id": {"required": True},
            "contest_categories_name": {"required": True},
            "age_category": {"required": True},
        }

    def create(self, validated_data):
        name_contest_categories: str = validated_data.pop(
            "contest_categories_name", None
        )

        age_category = validated_data.pop("age_category", None)

        age_categories = AgeCategories.objects.filter(id__in=age_category).all()

        contest_category, _ = ContestCategories.objects.get_or_create(
            name=name_contest_categories
        )

        validated_data["contest_categories_id"] = contest_category.id

        contest = Contest.objects.create(**validated_data)
        contest.age_category.add(*age_categories)

        user_id = self.context.get("user_id")

        Participant.objects.create(
            contest_id=contest.id, user_id=user_id, role=ParticipantRole.owner.value
        )

    def validate_region_id(self, region_id: int):
        if not Region.objects.filter(id=region_id).exists():
            raise ValidationError("Region does not exist")
        return region_id

    def validate_age_category(self, value):
        if not value:
            raise ValidationError("Age categories cannot be empty")

        existing_ids = set(
            AgeCategories.objects.filter(id__in=value).values_list("id", flat=True)
        )

        invalid_age_categories = [
            age_category_id
            for age_category_id in value
            if age_category_id not in existing_ids
        ]

        if invalid_age_categories:
            raise ValidationError(f"Invalid age category IDs: {invalid_age_categories}")

        return value


class UpdateBaseContestSerializer(ModelSerializer[Contest]):
    contest_categories_name = CharField(
        write_only=True, required=False, allow_blank=True
    )
    age_category = ListField(
        child=IntegerField(), write_only=True, required=False, allow_null=True
    )
    region_id = IntegerField(required=False, allow_null=True)

    class Meta:
        model = Contest
        fields = [
            "title",
            "description",
            "avatar",
            "link_to_rules",
            "organizer",
            "region_id",
            "age_category",
            "contest_categories_name",
        ]
        extra_kwargs = {
            "title": {"required": False},
            "description": {"required": False},
            "avatar": {"required": False},
            "link_to_rules": {"required": False},
            "organizer": {"required": False},
            "region_id": {"required": False},
            "age_category": {"required": False},
        }

    def validate_region_id(self, region_id: int):
        if not Region.objects.filter(id=region_id).exists():
            raise ValidationError("Region does not exist")
        return region_id

    def validate_age_category(self, value):
        if not value:
            raise ValidationError("Age categories cannot be empty")

        existing_ids = set(
            AgeCategories.objects.filter(id__in=value).values_list("id", flat=True)
        )

        invalid_age_categories = [
            age_category_id
            for age_category_id in value
            if age_category_id not in existing_ids
        ]

        if invalid_age_categories:
            raise ValidationError(f"Invalid age category IDs: {invalid_age_categories}")

        return value

    def update(self, instance, validated_data):
        category_name = validated_data.pop("contest_categories_name", None)
        if category_name:
            contest_category, _ = ContestCategories.objects.get_or_create(
                name=category_name
            )
            instance.contest_categories_id = contest_category.id

        age_category = validated_data.pop("age_category", None)

        if age_category:
            self._update_age_category(contest_id=instance.id)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _update_age_category(self, contest_id):
        age_category_ids = self.validated_data.pop("age_category", None)
        contest = Contest.objects.filter(id=contest_id).first()

        if not contest:
            raise ValidationError("Contest does not exist")

        current_age_category_ids = set(
            contest.age_category.values_list("id", flat=True)
        )
        new_age_category_ids = set(age_category_ids)

        age_category_to_add = new_age_category_ids - current_age_category_ids
        age_category_to_remove = current_age_category_ids - new_age_category_ids

        if age_category_to_add:
            contest.age_category.add(*age_category_to_add)

        if age_category_to_remove:
            contest.age_category.remove(*age_category_to_remove)

        return


class ContestChangeCriteriaSerializer(Serializer):
    criteria_list = ListField(child=JSONField(), required=True, write_only=True)

    def validate_criteria_list(self, data):
        if not data:
            raise ValidationError("criteria_list cannot be empty")
        return data

    def update_criteria_in_contest(self):
        contest = self.context.get("contest", None)
        criteria_list = self.validated_data.get("criteria_list")
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
                contest.criteria.values_list("id", flat=True)
            )

            criteria_to_remove: Set[int] = exists_criteria_in_db - set(
                existing_criteria
            )
            criteria_to_add: Set[int] = set(existing_criteria) - exists_criteria_in_db

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


class ContestChangeNominationSerializer(Serializer):
    nomination_list = ListField(child=JSONField(), required=True, write_only=True)

    def validate_nomination_list(self, data):
        if not data:
            raise ValidationError("nomination_list cannot be empty")
        return data

    def update_nominations_in_contest(self):
        contest = self.context.get("contest", None)
        nomination_list = self.validated_data.get("nomination_list")
        existing_nomination: List[int] = [
            nomination.get("id")
            for nomination in nomination_list
            if nomination.get("id") is not None
        ]

        new_nomination_list: List[Nominations] = [
            Nominations(
                name=nomination.get("name"), description=nomination.get("description")
            )
            for nomination in nomination_list
            if nomination.get("id") is None
        ]

        new_nomination_names: List[str] = [
            nomination.name for nomination in new_nomination_list
        ]

        with transaction.atomic():
            existing_name_nominations = set(
                Nominations.objects.filter(name__in=new_nomination_names).values_list(
                    "name", flat=True
                )
            )

            only_new_nominations: List[Nominations] = [
                nomination
                for nomination in new_nomination_list
                if nomination.name not in existing_name_nominations
            ]

            exists_nomination_in_db: Set[int] = set(
                contest.criteria.values_list("id", flat=True)
            )

            nominations_to_remove: Set[int] = exists_nomination_in_db - set(
                existing_nomination
            )
            nominations_to_add: Set[int] = (
                set(existing_nomination) - exists_nomination_in_db
            )

            if nominations_to_remove:
                contest.nominations.remove(*nominations_to_remove)

            if nominations_to_add:
                contest.nominations.add(*nominations_to_add)

            created_nominations: List[Nominations] = Nominations.objects.bulk_create(
                objs=only_new_nominations
            )
            if created_nominations:
                contest.nominations.add(*created_nominations)

            return None
