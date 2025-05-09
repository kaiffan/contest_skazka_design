from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField, CharField

from applications.enums import ApplicationStatus
from applications.models import Applications
from rest_framework.serializers import ModelSerializer, Serializer

from applications.validator import ApplicationValidator
from contests.models import Contest
from criteria.serializers import CriteriaSerializer
from participants.enums import ParticipantRole
from participants.models import Participant


class ApplicationSerializer(ModelSerializer[Applications]):
    class Meta:
        model = Applications
        fields = [
            "id",
            "name",
            "link_to_work",
            "annotation",
            "status",
            "rejection_reason",
            "contest_id",
            "user_id",
            "nomination",
        ]


class ApplicationWithCriteriaSerializer(ModelSerializer[Applications]):
    criteria = SerializerMethodField()

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

    def get_criteria(self, application: Applications):
        contest_criterias = application.contest.criteria.all()
        return CriteriaSerializer(contest_criterias, many=True).data


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
            exists_application = Applications.objects.filter(
                nomination_id=nomination_id, contest_id=contest_id, user_id=user.id
            ).exists()

            if exists_application:
                raise ValidationError("Application already exists")

            is_iternal_role = (
                Participant.objects.filter(contest_id=contest_id, user_id=user.id)
                .exclude(role=ParticipantRole.member.value)
                .exists()
            )

            if is_iternal_role:
                raise ValidationError("Participant role don't send application")

        return data

    def create(self, validated_data):
        user = self.context.get("user")
        contest_id = validated_data.get("contest_id")

        with transaction.atomic():
            contest: Contest = get_object_or_404(Contest, id=contest_id)
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


class ApproveApplicationSerializer(ModelSerializer[Applications]):
    class Meta:
        model = Applications
        fields = ["id"]
        extra_kwargs = {"id": {"required": True}}

    def validate(self, data):
        application_id = data.get("id")

        ApplicationValidator.validate_application(
            application_id=application_id,
            application_status=ApplicationStatus.accepted.value,
        )

        return data

    def update(self, instance, validated_data):
        instance.status = ApplicationStatus.accepted.value
        instance.rejection_reason = None
        instance.save()

        Participant.objects.create(
            user_id=instance.user_id, contest_id=instance.contest_id
        )


class RejectApplicationSerializer(ModelSerializer[Applications]):
    class Meta:
        model = Applications
        fields = ["id", "rejection_reason"]
        extra_kwargs = {
            "id": {"required": True},
            "rejection_reason": {"required": True},
        }

    def validate(self, data):
        application_id = data.get("id")

        ApplicationValidator.validate_application(
            application_id=application_id,
            application_status=ApplicationStatus.rejected.value,
        )

        rejection_reason = data.get("rejection_reason")

        if not rejection_reason:
            raise ValidationError("Rejection reason cannot be empty")

        return data

    def update(self, instance, validated_data):
        instance.status = ApplicationStatus.rejected.value
        instance.rejection_reason = validated_data.get("rejection_reason")
        instance.save()
