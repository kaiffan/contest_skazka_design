from rest_framework.exceptions import ValidationError

from applications.enums import ApplicationStatus
from applications.models import Applications
from rest_framework.serializers import ModelSerializer

from applications.validator import ApplicationValidator


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
            "user",
            "nomination",
        ]


class SendApplicationsSerializer(ModelSerializer[Applications]):
    class Meta:
        model = Applications
        fields = ["name", "annotation", "link_to_work", "nomination_id", "contest_id"]

    def validate(self, data):
        contest_id = data.get("contest_id")
        user_id = self.context.get("user_id")
        nomination_id = data.get("nomination_id")

        exists_application = Applications.objects.filter(
            nomination_id=nomination_id, contest_id=contest_id, user_id=user_id
        ).exists()

        if exists_application:
            raise ValidationError("Application already exists")

        return data

    def create(self, validated_data):
        user_id = self.context.get("user_id")

        return Applications.objects.create(user_id=user_id, **validated_data)


class ApproveApplicationSerializer(ModelSerializer[Applications]):
    class Meta:
        model = Applications
        fields = ["id"]

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


class RejectApplicationSerializer(ModelSerializer[Applications]):
    class Meta:
        model = Applications
        fields = ["id", "rejection_reason"]

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

    def update(self, instance: Applications, validated_data):
        instance.status = ApplicationStatus.rejected.value
        instance.rejection_reason = validated_data.get("rejection_reason")
        instance.save()
