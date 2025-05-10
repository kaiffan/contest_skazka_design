from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from applications.enums import ApplicationStatus
from applications.models import Applications
from criteria.models import Criteria
from work_rate.models import WorkRate


class WorkRateSerializer(ModelSerializer[WorkRate]):
    class Meta:
        model = WorkRate
        fields = ["criteria_id", "application_id", "rate"]

    def validate_application_id(self, value):
        try:
            application = Applications.objects.get(id=value)
        except Applications.DoesNotExist:
            raise ValidationError("Invalid application_id")
        if application.status != ApplicationStatus.accepted.value:
            raise ValidationError("Application status must be accepted")

        return value

    def validate(self, value):
        rate = value.get("rate", None)
        criteria_id = value.get("criteria_id", None)

        if not rate:
            raise ValidationError("Invalid rate")

        if not criteria_id:
            raise ValidationError("Invalid criteria_id")

        try:
            criteria = Criteria.objects.get(id=criteria_id)
        except Criteria.DoesNotExist:
            raise ValidationError("This criteria_id does not exist")

        if rate > criteria.max_points:
            raise ValidationError("Rate must be less than the criteria_max_points")

        if rate < criteria.min_points:
            raise ValidationError("Rate must be greater than the criteria's min_points")

        return value


class WorkRateAllSerializer(ModelSerializer[WorkRate]):
    class Meta:
        model = WorkRate
        fields = "__all__"
