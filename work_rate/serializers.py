from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from applications.enums import ApplicationStatus
from applications.models import Applications
from contests.models import Contest
from criteria.models import Criteria
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
        criteria_id = self.initial_data.get("criteria_id")
        if not criteria_id:
            raise ValidationError("criteria_id is required to validate rate")
        try:
            criteria = Criteria.objects.get(id=criteria_id)
        except Criteria.DoesNotExist:
            raise ValidationError("Criteria does not exist")
        if value < criteria.min_points or value > criteria.max_points:
            raise ValidationError(
                f"Rate must be between {criteria.min_points} and {criteria.max_points}"
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        return WorkRate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.rate = validated_data.get("rate", instance.rate)
        instance.save()

        return instance


class WorkRateAllSerializer(Serializer):
    application_id = IntegerField()
    total = IntegerField()
