from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from applications.enums import ApplicationStatus
from applications.models import Applications
from applications.serializers import ApplicationSerializer
from contest_criteria.models import ContestCriteria
from contests.models import Contest
from criteria.models import Criteria
from participants.models import Participant
from work_rate.models import WorkRate


class WorkRateSerializer(Serializer):
    application_id = IntegerField()
    criteria_id = IntegerField()
    rate = IntegerField()

    def validate_application_id(self, value):
        try:
            application = Applications.objects.get(id=value)
        except Applications.DoesNotExist:
            raise ValidationError("Invalid application_id")
        if application.status != ApplicationStatus.accepted.value:
            raise ValidationError("Application status must be accepted")

        return value

    def validate_criteria_id(self, value):
        contest: Contest = self.context.get("contest")

        if not value:
            raise ValidationError(detail="Invalid criteria_id", code=404)
        exists_in_contest = contest.criteria.filter(id=value).exists()

        if not exists_in_contest:
            raise ValidationError(
                detail="Does not exists criteria_id in contest", code=404
            )
        return value

    def validate_rate(self, value):
        init_data = self.initial_data

        for data in init_data:
            criteria_id = data.get("criteria_id", None)
            if not criteria_id:
                raise ValidationError("criteria_id is required to validate rate")
            try:
                contest_criteria = ContestCriteria.objects.get(id=criteria_id)
            except Criteria.DoesNotExist:
                raise ValidationError("Criteria does not exist")
            if (
                value < contest_criteria.min_points
                or value > contest_criteria.max_points
            ):
                raise ValidationError(
                    f"Rate must be between {contest_criteria.min_points} and {contest_criteria.max_points}"
                )
            return value

    @transaction.atomic
    def create(self, validated_data):
        jury_id = self.context.get("jury_id")
        return WorkRate.objects.create(jury_id=jury_id, **validated_data)

    def update(self, instance, validated_data):
        instance.rate = validated_data.get("rate", instance.rate)
        instance.save()

        return instance


class WorkRateAllSerializer(Serializer):
    application = ApplicationSerializer()
    total = IntegerField()

    def to_representation(self, instance):
        application = Applications.objects.get(id=instance["application_id"])
        return {
            "application": ApplicationSerializer(application).data,
            "total": instance["total"],
        }
