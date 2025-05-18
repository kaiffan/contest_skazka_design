from collections import defaultdict
from typing import List, Set
from datetime import date

from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (
    CharField,
    IntegerField,
    ListField,
    JSONField,
    SerializerMethodField,
)
from rest_framework.serializers import ModelSerializer, Serializer

from age_categories.models import AgeCategories
from age_categories.serializers import AgeCategoriesSerializer
from applications.models import Applications
from contest_categories.models import ContestCategories
from contest_stage.models import ContestStage
from contest_stage.serializers import ContestStageSerializer
from contests.models import Contest
from contests.utils import get_current_contest_stage
from contests_contest_stage.models import ContestsContestStage
from criteria.models import Criteria
from criteria.serializers import CriteriaSerializer
from nomination.models import Nominations
from nomination.serializers import NominationsSerializer
from participants.enums import ParticipantRole
from participants.models import Participant
from participants.serializers import ParticipantSerializer
from regions.models import Region
from winners.models import Winners


class ContestByIdSerializer(ModelSerializer[Contest]):
    jury = SerializerMethodField()
    criteria = SerializerMethodField()
    nomination = SerializerMethodField()
    age_categories = SerializerMethodField()
    contest_stage = SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            "title",
            "description",
            "link_to_rules",
            "avatar",
            "organizer",
            "is_draft",
            "nomination",
            "criteria",
            "age_categories",
            "contest_stage",
            "jury",
        ]

    def get_jury(self, instance):
        jury_list = Participant.objects.filter(
            contest_id=instance.id, role=ParticipantRole.jury.value
        ).all()
        return ParticipantSerializer(jury_list, many=True).data

    def get_criteria(self, instance):
        criteria_list = instance.criteria.all()
        return CriteriaSerializer(criteria_list, many=True).data

    def get_nomination(self, instance):
        nomination_list = instance.nominations.all()
        return NominationsSerializer(nomination_list, many=True).data

    def get_age_categories(self, instance):
        age_category_list = instance.age_category.all()
        return AgeCategoriesSerializer(age_category_list, many=True).data

    def get_contest_stage(self, instance):
        contest_stage_list = instance.contest_stage.all()
        return ContestStageSerializer(contest_stage_list, many=True).data


class ContestAllSerializer(ModelSerializer[Contest]):
    contest_stage = SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            "title",
            "avatar",
            "contest_categories",
            "contest_stage",
        ]

    def get_contest_stage(self, contest):
        return get_current_contest_stage(contest=contest)


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

            created_nominations: List[Nominations] = Nominations.objects.bulk_create(
                objs=only_new_nominations
            )

            if created_nominations:
                contest.nominations.add(*created_nominations)

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

            return None


# TODO: доделать сериалайзер согласно новым условиям
class ContestChangeStageSerializer(Serializer):
    contest_stage_list = ListField(child=JSONField(), required=True, write_only=True)

    def validate_contest_stage_list(self, data):
        if not data:
            raise ValidationError("contest_stage_list cannot be empty")

        stages_with_dates = []

        for contest_stage in data:
            start_date_str: str = contest_stage.get("start_date")
            end_date_str: str = contest_stage.get("end_date")

            if not start_date_str or not end_date_str:
                raise ValidationError("date_start or date_end cannot be empty")

            try:
                start_date: date = date.fromisoformat(start_date_str)
                end_date: date = date.fromisoformat(end_date_str)
            except ValueError:
                raise ValidationError(
                    f"Invalid date format. Use YYYY-MM-DD. Got: start_date={start_date_str}, end_date={end_date_str}"
                )

            if start_date >= end_date:
                raise ValidationError("date_start must be before date_end")

            stages_with_dates.append(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )

        previous_end = None
        for contest_stage in stages_with_dates:
            current_stage_start: date = contest_stage.get("start_date")
            current_stage_end: date = contest_stage.get("end_date")

            if previous_end is not None:
                if previous_end > current_stage_start:
                    raise ValidationError(
                        f"Stages have overlapping time ranges: previous end_date "
                        f"({previous_end}) > next start_date ({current_stage_start})"
                    )

            previous_end = current_stage_end

        return data

    def change_contest_stages_in_contest(self):
        contest = self.context.get("contest", None)
        contest_stage_list = self.validated_data.get("contest_stage_list", None)

        if not contest_stage_list:
            raise ValidationError(detail="contest_stage_list cannot be empty", code=404)

        existing_stages = ContestsContestStage.objects.filter(contest=contest)
        existing_stages_data = {stage.stage_id: stage for stage in existing_stages}

        stages_to_create = []
        stages_to_update = []

        for contest_stage in contest_stage_list:
            stage_id = contest_stage.get("stage_id")
            start_date = contest_stage.get("start_date")
            end_date = contest_stage.get("end_date")

            if stage_id in existing_stages_data:
                stage = existing_stages_data[stage_id]
                stage.start_date = start_date
                stage.end_date = end_date
                stages_to_update.append(stage)
            else:
                stages_to_create.append(
                    ContestsContestStage(
                        contest=contest,
                        stage_id=stage_id,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

        if stages_to_create:
            ContestsContestStage.objects.bulk_create(objs=stages_to_create)

        if stages_to_update:
            ContestsContestStage.objects.bulk_update(
                objs=stages_to_update, fields=["start_date", "end_date"]
            )

        return


class ContestWinnerSerializer(Serializer):
    def assign_places(self, winners: List[Winners]) -> List[Winners]:
        """
        Присваивает места участникам, учитывая одинаковые суммы баллов.
        :param winners: Список объектов Winners, не отсортированный
        :return: Список объектов Winners с присвоенными местами
        """
        if not winners:
            return []

        groups = defaultdict(list)

        for winner in winners:
            app = winner.application
            key = (app.nomination_id, app.age_category)
            groups[key].append(winner)

        updated_winners = []

        for key, group_winners in groups.items():
            sorted_group = sorted(group_winners, key=lambda w: w.sum_rate, reverse=True)

            current_place = 0
            previous_score = None

            for idx, winner in enumerate(sorted_group, start=1):
                if winner.sum_rate != previous_score:
                    current_place += 1
                    previous_score = winner.sum_rate
                winner.place = current_place
                updated_winners.append(winner)

        return updated_winners

    def change_winners_by_contest(self):
        contest: Contest = self.context.get("contest", None)

        with transaction.atomic():
            applications = Applications.objects.filter(contest_id=contest.id).annotate(
                total_score=Sum("workrate__rate")
            )

            existing_winners = Winners.objects.filter(contest=contest).in_bulk(
                field_name="application_id"
            )

            to_update: List[Winners] = []
            to_create: List[Winners] = []

            for application in applications:
                total_score = application.total_score_application
                winner = existing_winners.get(application.pk, None)

                if not winner:
                    to_create.append(
                        Winners(
                            contest=contest.id,
                            application=application.id,
                            rate=total_score,
                        )
                    )
                    continue

                if winner.sum_rate != total_score:
                    winner.sum_rate = total_score
                    to_update.append(winner)

            if to_update:
                Winners.objects.bulk_update(objs=to_update, fields=["rate"])

            if to_create:
                Winners.objects.bulk_create(objs=to_create)

            all_winners_by_contest = Winners.objects.filter(
                contest=contest
            ).select_related("application")

            updated_winners = self.assign_places(list(all_winners_by_contest))
            Winners.objects.bulk_update(updated_winners, fields=["place"])
