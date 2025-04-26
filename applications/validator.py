from rest_framework.serializers import ValidationError

from applications.models import Applications


class ApplicationValidator:
    @staticmethod
    def validate_application(application_id, application_status):
        application = Applications.objects.filter(id=application_id).first()

        if not application:
            return ValidationError("Application does not exist")

        if application.status == application_status:
            raise ValidationError(f"Application already {application_status}")
