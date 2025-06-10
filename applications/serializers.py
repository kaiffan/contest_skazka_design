from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (
    SerializerMethodField,
    IntegerField,
    CharField,
    ListField,
)

from applications.enums import ApplicationStatus
from applications.models import Applications
from rest_framework.serializers import ModelSerializer, Serializer

from applications.validator import ApplicationValidator
from contest_criteria.models import ContestCriteria
from contest_criteria.serializers import ContestCriteriaFullSerializer
from contest_nominations.models import ContestNominations
from contest_nominations.serializers import ContestNominationsSerializer
from contests.models import Contest
from participants.enums import ParticipantRole
from participants.models import Participant


class ApplicationSerializer(ModelSerializer[Applications]):
    contest_title = SerializerMethodField()
    nomination_name = SerializerMethodField()

    class Meta:
        model = Applications
        fields = [
            "id",
            "name",
            "link_to_work",
            "annotation",
            "status",
            "rejection_reason",
            "contest_title",
            "contest_id",
            "nomination_name",
            "age_category",
            "user_id",
        ]

    def get_contest_title(self, instance: Applications):
        return instance.contest.title

    def get_nomination_name(self, instance: Applications):
        return instance.nomination.name


class ApplicationWithCriteriaSerializer(ModelSerializer[Applications]):
    criteria = SerializerMethodField()
    nomination = SerializerMethodField()

    class Meta:
        model = Applications
        fields = [
            "id",
            "name",
            "link_to_work",
            "annotation",
            "status",
            "rejection_reason",
            "user_id",
            "nomination",
            "contest_id",
            "criteria",
        ]

    def get_criteria(self, application):
        contest_criterias = ContestCriteria.objects.filter(
            contest_id=application.contest_id
        ).all()
        return ContestCriteriaFullSerializer(instance=contest_criterias, many=True).data

    def get_nomination(self, application):
        contest_nominations = ContestNominations.objects.filter(
            contest_id=application.contest_id,
            nomination_id=application.nomination_id,
        ).get()

        return ContestNominationsSerializer(instance=contest_nominations).data


class SendApplicationsSerializer(Serializer):
    name = CharField(required=True)
    annotation = CharField(required=True)
    link_to_work = CharField(required=False, allow_blank=True, allow_null=True)
    nomination_id = IntegerField(required=True)
    contest_id = IntegerField(required=True)

    def validate(self, data):
        contest_id = data.get("contest_id")
        user = self.context.get("user")
        nomination_id = data.get("nomination_id")

        with transaction.atomic():
            contest = Contest.objects.get(id=contest_id)

            if not contest:
                raise ValidationError(
                    detail={"error": "Contest does not exist"}, code=404
                )

            exists_application = Applications.objects.filter(
                nomination_id=nomination_id, contest_id=contest.id, user_id=user.id
            ).exists()

            contest_region: str = contest.region.name
            user_region = user.region.name

            if not (contest_region == user_region or contest_region == "Онлайн"):
                raise ValidationError(
                    detail={"error": "This application does not belong to this region"},
                    code=403,
                )

            if exists_application:
                raise ValidationError(detail={"error": "Application already exists"})

            is_iternal_role = (
                Participant.objects.filter(contest_id=contest.id, user_id=user.id)
                .exclude(role=ParticipantRole.member.value)
                .exists()
            )

            if is_iternal_role:
                raise ValidationError(
                    detail={"error": "Participant role don't send application"},
                    code=400,
                )

        return data

    def create(self, validated_data):
        user = self.context.get("user")
        contest_id = validated_data.get("contest_id")

        with transaction.atomic():
            contest = get_object_or_404(Contest, id=contest_id)
            count_full_age: int = user.get_full_age()
            matching_age_category_name = contest.age_category.filter(
                start_age__lte=count_full_age,
                end_age__gte=count_full_age,
            ).first()

            if not matching_age_category_name:
                raise ValidationError("Ваш возраст не подходит ни под одну категорию.")

            application = Applications.objects.create(
                user_id=user.id,
                age_category=matching_age_category_name.name,
                **validated_data,
            )
        return application


class ApproveApplicationSerializer(Serializer):
    application_ids = ListField(child=IntegerField(), required=True, allow_empty=False)

    def validate_application_ids(self, value):
        validated_instances = []

        for app_id in value:
            instance = ApplicationValidator.validate_application(
                application_id=app_id,
                application_status=ApplicationStatus.accepted.value,
            )
            validated_instances.append(instance)

        self.instance = validated_instances
        return value

    @transaction.atomic
    def update(self, instances, validated_data):
        approved_applications = []

        for application in instances:
            application.status = ApplicationStatus.accepted.value
            application.rejection_reason = None
            application.save(update_fields=["status", "rejection_reason"])

            Participant.objects.create(
                user_id=application.user_id,
                contest_id=application.contest_id,
                role=ParticipantRole.member.value,
            )

            approved_applications.append(application)

        return approved_applications

    def save(self, **kwargs):
        return self.update(self.instance, self.validated_data)


class RejectApplicationSerializer(Serializer):
    application_id = IntegerField(required=True)
    rejection_reason = CharField(required=True)

    def validate_application_id(self, application_id):
        instance = ApplicationValidator.validate_application(
            application_id=application_id,
            application_status=ApplicationStatus.rejected.value,
        )

        self.instance = instance
        return application_id

    def update(self, instance, validated_data):
        instance.status = ApplicationStatus.rejected.value
        instance.rejection_reason = validated_data.get("rejection_reason")
        instance.save(update_fields=["status", "rejection_reason"])

        return instance

    def save(self, **kwargs):
        return self.update(self.instance, self.validated_data)


class UpdateApplicationSerializer(ModelSerializer[Applications]):
    class Meta:
        model = Applications
        fields = ["name", "annotation", "link_to_work"]
