from django.db import transaction
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, ListField, SerializerMethodField
from rest_framework.serializers import Serializer

from applications.enums import ApplicationStatus
from applications.models import Applications
from applications.serializers import ApplicationSerializer
from contest_criteria.models import ContestCriteria
from work_rate.models import WorkRate


class RateItemSerializer(Serializer):
    criteria_id = IntegerField()
    rate = IntegerField()


class WorkRateSerializer(Serializer):
    application_id = IntegerField()
    rates = ListField(child=RateItemSerializer(), allow_empty=False)

    def validate_application_id(self, value):
        try:
            application = Applications.objects.get(id=value)
        except Applications.DoesNotExist:
            raise ValidationError(detail={"error": "Invalid application_id"}, code=400)
        if application.status != ApplicationStatus.accepted.value:
            raise ValidationError(
                detail={"error": "Application status must be accepted"}, code=400
            )

        return value

    def validate_rates(self, value):
        contest = self.context.get("contest")

        for item in value:
            criteria_id = item.get("criteria_id")
            rate = item.get("rate")

            if not isinstance(criteria_id, int):
                raise ValidationError(
                    detail={"error": "criteria_id must be an integer"}, code="invalid"
                )

            if not isinstance(rate, int):
                raise ValidationError(
                    detail={"error": "rate must be an integer"}, code="invalid"
                )

            try:
                contest_criteria = ContestCriteria.objects.get(
                    criteria_id=criteria_id, contest=contest
                )
            except ContestCriteria.DoesNotExist:
                raise ValidationError(
                    detail={
                        "error": f"Criteria with id {criteria_id} does not exist in this contest"
                    },
                    code="invalid",
                )

            if not (contest_criteria.min_points <= rate <= contest_criteria.max_points):
                raise ValidationError(
                    detail={
                        "error": f"Rate for criteria {criteria_id} must be between "
                        f"{contest_criteria.min_points} and {contest_criteria.max_points}"
                    },
                    code="invalid",
                )

        return value

    @transaction.atomic
    def create(self, validated_data):
        application_id = validated_data.get("application_id", None)
        rates = validated_data.get("rates", None)
        jury_id = self.context.get("jury_id", None)

        criteria_ids = [rate.get("criteria_id") for rate in rates]
        existing_work_rates = set(
            WorkRate.objects.filter(
                application_id=application_id, criteria_id__in=criteria_ids
            ).values_list("criteria_id", flat=True)
        )

        duplicates = existing_work_rates.intersection(criteria_ids)
        if not duplicates:
            return WorkRate.objects.bulk_create(
                [
                    WorkRate(
                        jury_id=jury_id,
                        application_id=application_id,
                        criteria_id=item["criteria_id"],
                        rate=item["rate"],
                    )
                    for item in rates
                ]
            )
        raise ValidationError(
            {
                "error": f"Оценки для критериев {', '.join(map(str, duplicates))} уже существуют. Обновите их."
            }
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        jury_id = self.context.get("jury_id")
        contest = self.context.get("contest")
        rates = validated_data.get("rates", None)
        application_id = validated_data.get("application_id", None)

        updated_instances = []
        missing_ids = []

        for item in rates:
            criteria_id = item.get("criteria_id")
            new_rate = item.get("rate")

            try:
                instance = WorkRate.objects.get(
                    application_id=application_id,
                    criteria_id=criteria_id,
                    application__contest_id=contest.id,
                )
            except WorkRate.DoesNotExist:
                missing_ids.append(criteria_id)
                continue

            if instance.rate != new_rate:
                instance.rate = new_rate

            if jury_id and instance.jury_id != jury_id:
                instance.jury_id = jury_id

            instance.save()

            updated_instances.append(instance)

        if missing_ids:
            raise ValidationError(
                {
                    "error": f"Не найдены оценки для критериев: {', '.join(map(str, missing_ids))}"
                }
            )

        return WorkRate.objects.bulk_update(objs=updated_instances, fields=["rate"])


class WorkRateContestAllSerializer(Serializer):
    application = ApplicationSerializer()
    total = IntegerField()

    def to_representation(self, instance):
        application = Applications.objects.get(id=instance["application_id"])
        return {
            "application": ApplicationSerializer(application).data,
            "total": instance["total"],
        }


class ApplicationRatesSerializer(ModelSerializer[Applications]):
    rates = SerializerMethodField()

    class Meta:
        model = Applications
        fields = ["id", "rates"]

    def get_rates(self, application):
        work_rates = WorkRate.objects.filter(application=application)

        return [
            {
                "criteria_id": work_rate.criteria.id,
                "criteria_name": work_rate.criteria.name,
                "rate": work_rate.rate,
            }
            for work_rate in work_rates
        ]
