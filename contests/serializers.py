from collections import defaultdict
from typing import List, Dict
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
from applications.enums import ApplicationStatus
from applications.models import Applications
from contest_categories.models import ContestCategories
from contest_criteria.models import ContestCriteria
from contest_criteria.serializers import ContestCriteriaSerializer
from contest_file_constraints.models import ContestFileConstraints
from contest_file_constraints.serializers import ContestFileConstraintsSerializer
from contest_nominations.models import ContestNominations
from contest_nominations.serializers import ContestNominationsSerializer
from contests.models import Contest
from contests.utils import get_current_contest_stage
from contests_contest_stage.models import ContestsContestStage
from contests_contest_stage.serializers import ContestsContestStageSerializer
from criteria.models import Criteria
from file_constraints.models import FileConstraint
from nomination.models import Nominations
from participants.enums import ParticipantRole
from participants.models import Participant
from participants.serializers import PartisipantContestSerializer
from winners.models import Winners


class ContestByIdSerializer(ModelSerializer[Contest]):
    jury = SerializerMethodField()
    org_committee = SerializerMethodField()
    criteria = SerializerMethodField()
    file_constraint = SerializerMethodField()
    contest_category = SerializerMethodField()
    nomination = SerializerMethodField()
    age_categories = SerializerMethodField()
    contest_stage = SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            "id",
            "title",
            "description",
            "link_to_rules",
            "avatar",
            "organizer",
            "is_draft",
            "is_deleted",
            "is_published",
            "nomination",
            "criteria",
            "age_categories",
            "contest_stage",
            "jury",
            "org_committee",
            "prizes",
            "contacts_for_participants",
            "file_constraint",
            "contest_category",
        ]

    def get_file_constraint(self, instance):
        contest_file_constraints = ContestFileConstraints.objects.filter(
            contest=instance
        ).all()
        return ContestFileConstraintsSerializer(
            instance=contest_file_constraints, many=True
        ).data

    def get_org_committee(self, instance):
        org_committee_list = Participant.objects.filter(
            contest_id=instance.id, role=ParticipantRole.org_committee.value
        ).all()
        return PartisipantContestSerializer(instance=org_committee_list, many=True).data

    def get_jury(self, instance):
        jury_list = Participant.objects.filter(
            contest_id=instance.id, role=ParticipantRole.jury.value
        ).all()
        return PartisipantContestSerializer(instance=jury_list, many=True).data

    def get_contest_category(self, instance):
        return instance.contest_category.name

    def get_criteria(self, instance):
        criteria_list = ContestCriteria.objects.filter(contest_id=instance.id).all()
        return ContestCriteriaSerializer(instance=criteria_list, many=True).data

    def get_nomination(self, instance):
        nomination_list = ContestNominations.objects.filter(
            contest_id=instance.id
        ).all()
        return ContestNominationsSerializer(instance=nomination_list, many=True).data

    def get_age_categories(self, instance):
        age_category_list = instance.age_category.all()
        return AgeCategoriesSerializer(instance=age_category_list, many=True).data

    def get_contest_stage(self, instance):
        contests_contest_stage_list = ContestsContestStage.objects.filter(
            contest_id=instance.id
        ).all()
        return ContestsContestStageSerializer(
            instance=contests_contest_stage_list, many=True
        ).data


class ContestAllSerializer(ModelSerializer[Contest]):
    contest_stage = SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            "id",
            "title",
            "avatar",
            "contest_category",
            "contest_stage",
        ]

    def get_contest_stage(self, contest):
        return get_current_contest_stage(contest_id=contest.id)


class ContestAllOwnerSerializer(ModelSerializer[Contest]):
    count_application = SerializerMethodField()
    count_jury = SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            "id",
            "title",
            "avatar",
            "count_application",
            "count_jury",
            "is_draft",
            "is_published",
            "is_deleted",
        ]

    def get_count_application(self, contest):
        return Applications.objects.filter(contest=contest).count()

    def get_count_jury(self, contest):
        return Participant.objects.filter(
            contest=contest, role=ParticipantRole.jury.value
        ).count()


class ContestAllJurySerializer(ModelSerializer[Contest]):
    current_stage = SerializerMethodField()
    count_application = SerializerMethodField()

    class Meta:
        model = Contest
        fields = ["id", "avatar", "title", "current_stage", "count_application"]

    def get_count_application(self, contest):
        return Applications.objects.filter(
            status=ApplicationStatus.accepted.value, contest=contest
        ).count()

    def get_current_stage(self, contest):
        return get_current_contest_stage(contest_id=contest.id)


class CreateBaseContestSerializer(ModelSerializer[Contest]):
    contest_category_name = CharField(write_only=True)
    age_category = ListField(child=IntegerField(), write_only=True)

    class Meta:
        model = Contest
        fields = [
            "title",
            "description",
            "avatar",
            "link_to_rules",
            "organizer",
            "prizes",
            "contacts_for_participants",
            "contest_category_name",
            "age_category",
        ]
        extra_kwargs = {
            "title": {"required": True},
            "description": {"required": True},
            "avatar": {"required": False},
            "link_to_rules": {"required": False},
            "organizer": {"required": True},
            "prizes": {"required": False},
            "contacts_for_participants": {"required": False},
            "contest_category_name": {"required": True},
            "age_category": {"required": True},
        }

    def create(self, validated_data) -> Contest:
        name_contest_categories: str = validated_data.pop("contest_category_name", None)

        age_category = validated_data.pop("age_category", None)

        age_categories = AgeCategories.objects.filter(id__in=age_category).all()

        contest_category, _ = ContestCategories.objects.get_or_create(
            name=name_contest_categories
        )

        contest = Contest.objects.create(
            contest_category_id=contest_category.id, **validated_data
        )
        contest.age_category.add(*age_categories)

        user_id = self.context.get("user_id")

        Participant.objects.create(
            contest_id=contest.id, user_id=user_id, role=ParticipantRole.owner.value
        )

        return contest

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
            raise ValidationError(
                detail={"error": f"Invalid age category IDs: {invalid_age_categories}"},
                code=400,
            )

        return value


class UpdateBaseContestSerializer(Serializer):
    title = CharField(required=False)
    description = CharField(required=False)
    avatar = CharField(required=False)
    link_to_rules = CharField(required=False)
    prizes = CharField(required=False)
    contacts_for_participants = CharField(required=False)
    organizer = CharField(required=False)
    contest_category_name = CharField(required=False)
    age_category = ListField(child=IntegerField(), required=False)

    def validate_age_category(self, value):
        if not value:
            raise ValidationError(
                detail={"error": "Age categories cannot be empty"}, code=400
            )

        existing_ids = set(
            AgeCategories.objects.filter(id__in=value).values_list("id", flat=True)
        )

        invalid_age_categories = [
            age_category_id
            for age_category_id in value
            if age_category_id not in existing_ids
        ]

        if invalid_age_categories:
            raise ValidationError(
                detail={"error": f"Invalid age category IDs: {invalid_age_categories}"},
                code=400,
            )

        return value

    def update(self, instance, validated_data):
        category_name = validated_data.pop("contest_category_name", None)
        age_category = validated_data.pop("age_category", None)

        if category_name:
            contest_category, _ = ContestCategories.objects.get_or_create(
                name=category_name
            )
            instance.contest_category_id = contest_category.id

        if age_category:
            self._update_age_category(
                contest_id=instance.id, age_category_ids=age_category
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _update_age_category(self, contest_id, age_category_ids):
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

        for idx, criteria in enumerate(data):
            min_points = criteria.get("min_points")
            max_points = criteria.get("max_points")

            if min_points is None or max_points is None:
                raise ValidationError(
                    detail={
                        f"criteria_list[{idx}]": "Each criteria must contain 'min_points' and 'max_points'"
                    },
                    code=400,
                )

            if min_points > max_points:
                raise ValidationError(
                    detail={
                        f"criteria_list[{idx}]": "'min_points' must be less than or equal to 'max_points'"
                    },
                    code=400,
                )

        return data

    def update_criteria_in_contest(self):
        contest = self.context.get("contest", None)
        criteria_list = self.validated_data.get("criteria_list", [])

        criteria_data_by_name = {
            criteria["name"]: {
                "description": criteria.get("description", ""),
                "min_points": criteria.get("min_points", 0),
                "max_points": criteria.get("max_points", 10),
            }
            for criteria in criteria_list
            if criteria.get("name")
        }

        result = {"added": [], "removed": [], "updated": []}
        input_names = set(criteria_data_by_name.keys())

        with transaction.atomic():
            existing_criteria = Criteria.objects.filter(name__in=input_names)
            existing_names_in_db = {c.name for c in existing_criteria}

            new_names = input_names - existing_names_in_db
            created_criteria = Criteria.objects.bulk_create(
                [Criteria(name=name) for name in new_names]
            )

            all_criteria = list(existing_criteria) + list(created_criteria)
            name_to_id = {c.name: c.id for c in all_criteria}

            current_relations = ContestCriteria.objects.filter(
                contest=contest
            ).select_related("criteria")
            current_names = {rel.criteria.name for rel in current_relations}

            current_desc_map = {
                rel.criteria.name: {
                    "description": rel.description,
                    "min_points": rel.min_points,
                    "max_points": rel.max_points,
                }
                for rel in current_relations
            }

            to_add = input_names - current_names
            to_remove = current_names - input_names
            to_check_update = input_names & current_names

            to_update = [
                name
                for name in to_check_update
                if (
                    current_desc_map[name]["description"]
                    != criteria_data_by_name[name]["description"]
                    or current_desc_map[name]["min_points"]
                    != criteria_data_by_name[name]["min_points"]
                    or current_desc_map[name]["max_points"]
                    != criteria_data_by_name[name]["max_points"]
                )
            ]

            result["added"] = list(to_add)
            result["removed"] = list(to_remove)
            result["updated"] = list(to_update)

            if to_remove:
                ContestCriteria.objects.filter(
                    contest=contest, criteria__name__in=to_remove
                ).delete()

            if to_add:
                ContestCriteria.objects.bulk_create(
                    [
                        ContestCriteria(
                            contest=contest,
                            criteria_id=name_to_id[name],
                            description=criteria_data_by_name[name]["description"],
                            min_points=criteria_data_by_name[name]["min_points"],
                            max_points=criteria_data_by_name[name]["max_points"],
                        )
                        for name in to_add
                    ]
                )

            if to_update:
                updated_relations = []
                for name in to_update:
                    relation = ContestCriteria.objects.get(
                        contest=contest, criteria__name=name
                    )
                    relation.description = criteria_data_by_name[name]["description"]
                    relation.min_points = criteria_data_by_name[name]["min_points"]
                    relation.max_points = criteria_data_by_name[name]["max_points"]
                    updated_relations.append(relation)

                ContestCriteria.objects.bulk_update(
                    objs=updated_relations,
                    fields=["description", "min_points", "max_points"],
                )

        return result


class ContestChangeNominationSerializer(Serializer):
    nomination_list = ListField(child=JSONField(), required=True, write_only=True)

    def validate_nomination_list(self, data):
        if not data:
            raise ValidationError(
                detail={"error": "nomination_list cannot be empty"}, code=400
            )
        return data

    def update_nominations_in_contest(self):
        contest = self.context.get("contest", None)
        nomination_list = self.validated_data.get("nomination_list")

        nomination_dict: Dict[str, str] = {
            nomination["name"]: nomination.get("description", "")
            for nomination in nomination_list
            if nomination.get("name")
        }

        input_names = set(nomination_dict.keys())
        result = {"added": [], "removed": [], "updated": []}

        with transaction.atomic():
            existing_noms_in_db = Nominations.objects.filter(name__in=input_names)
            existing_names_in_db = {nom.name for nom in existing_noms_in_db}

            new_names = input_names - existing_names_in_db
            created_noms = Nominations.objects.bulk_create(
                [Nominations(name=name) for name in new_names]
            )

            all_nominations = {
                nom.name: nom.id
                for nom in list(existing_noms_in_db) + list(created_noms)
            }

            current_relations = ContestNominations.objects.filter(
                contest=contest
            ).select_related("nomination")

            current_names = {rel.nomination.name for rel in current_relations}
            current_desc_map = {
                rel.nomination.name: rel.description for rel in current_relations
            }

            to_add = input_names - current_names
            to_remove = current_names - input_names
            to_check_update = input_names & current_names
            to_update = [
                name
                for name in to_check_update
                if nomination_dict[name] != current_desc_map.get(name)
            ]

            result["added"] = list(to_add)
            result["removed"] = list(to_remove)
            result["updated"] = list(to_update)

            if to_remove:
                ContestNominations.objects.filter(
                    contest=contest, nomination__name__in=to_remove
                ).delete()
                result["removed"] = list(to_remove)

            if to_add:
                ContestNominations.objects.bulk_create(
                    [
                        ContestNominations(
                            contest=contest,
                            nomination_id=all_nominations[name],
                            description=nomination_dict[name],
                        )
                        for name in to_add
                    ]
                )
                result["added"] = list(to_add)

            if to_update:
                for name in to_update:
                    ContestNominations.objects.filter(
                        contest=contest, nomination__name=name
                    ).update(description=nomination_dict[name])

        return result


class ContestChangeStageSerializer(Serializer):
    contest_stage_list = ListField(child=JSONField(), required=True, write_only=True)

    def validate_contest_stage_list(self, data):
        if not data:
            raise ValidationError(
                detail={"error": "contest_stage_list cannot be empty"}, code=400
            )

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
                    detail={
                        "error": f"Invalid date format. Use YYYY-MM-DD. Got: start_date={start_date_str}, end_date={end_date_str}"
                    },
                    code=400,
                )

            if start_date >= end_date:
                raise ValidationError(
                    detail={"error": "date_start must be before date_end"}, code=400
                )

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
                        detail={
                            "error": f"Stages have overlapping time ranges: previous end_date "
                            f"({previous_end}) > next start_date ({current_stage_start})"
                        },
                        code=400,
                    )

            previous_end = current_stage_end

        return data

    def change_contest_stages_in_contest(self):
        contest = self.context.get("contest", None)
        contest_stage_list = self.validated_data.get("contest_stage_list", None)
        result = {"added": [], "updated": []}

        if not contest_stage_list:
            raise ValidationError(
                detail={"error": "contest_stage_list cannot be empty"}, code=404
            )

        existing_stages = ContestsContestStage.objects.filter(contest=contest).all()

        if not existing_stages.exists():
            stages_to_create = []

            for item in contest_stage_list:
                stage_id = item.get("stage_id")
                start_date = item.get("start_date")
                end_date = item.get("end_date")

                stages_to_create.append(
                    ContestsContestStage(
                        contest=contest,
                        stage_id=stage_id,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

            ContestsContestStage.objects.bulk_create(objs=stages_to_create)
            result["added"] = [stage.stage_id for stage in stages_to_create]
            return result

        stages_to_update = []
        existing_stages_data = {stage.stage_id: stage for stage in existing_stages}

        for contest_stage in contest_stage_list:
            stage_id = contest_stage.get("stage_id")
            start_date = contest_stage.get("start_date")
            end_date = contest_stage.get("end_date")

            if stage_id in existing_stages_data:
                stage = existing_stages_data[stage_id]
                stage.start_date = start_date
                stage.end_date = end_date
                stages_to_update.append(stage)

        if stages_to_update:
            ContestsContestStage.objects.bulk_update(
                objs=stages_to_update, fields=["start_date", "end_date"]
            )
        result["updated"] = [stage.stage_id for stage in stages_to_update]

        return result


class FileConstraintChangeSerializer(Serializer):
    file_constraint_ids = ListField(child=JSONField(), required=True, write_only=True)

    def validate_file_constraint_ids(self, value):
        if not value:
            raise ValidationError(
                detail={"error": "Список ограничений не может быть пустым."}, code=400
            )
        if len(value) > 3:
            raise ValidationError(
                detail={"error": "Нельзя указать больше 3 ограничений."}, code=400
            )

        received_ids = [item.get("id") for item in value]

        existing_ids = list(
            FileConstraint.objects.filter(id__in=received_ids).values_list(
                "id", flat=True
            )
        )

        missing_ids = set(received_ids) - set(existing_ids)

        if not missing_ids:
            return value

        raise ValidationError(
            detail={"error": f"Ограничения с ID {missing_ids} не существуют."}, code=400
        )

    def update(self, instance, validated_data):
        file_constraint_ids = validated_data.get("file_constraint_ids", [])

        new_constraint_ids = set(constraint["id"] for constraint in file_constraint_ids)

        current_constraints = instance.file_constraint.all()
        current_constraint_ids = set(
            constraint.id for constraint in current_constraints
        )

        to_add = new_constraint_ids - current_constraint_ids
        to_remove = current_constraint_ids - new_constraint_ids

        if to_add:
            instance.file_constraint.add(*to_add)

        if to_remove:
            instance.file_constraint.remove(*to_remove)

        return instance


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

            existing_winners = {
                winner.application_id: winner
                for winner in Winners.objects.filter(contest=contest).select_related(
                    "application"
                )
            }

            to_update: List[Winners] = []
            to_create: List[Winners] = []

            for application in applications:
                total_score = application.total_score
                winner = existing_winners.get(application.pk, None)

                if not winner:
                    to_create.append(
                        Winners(
                            contest=contest,
                            application=application,
                            sum_rate=total_score,
                        )
                    )
                    continue

                if winner.sum_rate != total_score:
                    winner.sum_rate = total_score
                    to_update.append(winner)

            if to_update:
                Winners.objects.bulk_update(objs=to_update, fields=["sum_rate"])

            if to_create:
                Winners.objects.bulk_create(objs=to_create)

            all_winners_by_contest = Winners.objects.filter(
                contest=contest
            ).select_related("application")

            updated_winners = self.assign_places(list(all_winners_by_contest))
            Winners.objects.bulk_update(objs=updated_winners, fields=["place"])
