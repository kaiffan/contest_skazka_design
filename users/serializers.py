from datetime import date

from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField, CharField, EmailField, URLField, DateField
from rest_framework.serializers import Serializer, ModelSerializer

from authentication.models import Users
from competencies.models import Competencies
from competencies.serializers import CompetenciesSerializer


class ContestDataUpdateSerializer(Serializer):
    competencies = ListField(child=CharField(), required=True)
    education_or_work = CharField(max_length=255, required=True)

    def validate_competencies(self, value):
        if not value:
            raise ValidationError(
                detail={"error": "Competencies cannot be empty"}, code=400
            )

        if len(value) != len(set(value)):
            raise ValidationError(
                detail={"error": "Competencies cannot contain duplicate competencies"},
                code=400,
            )

        return value

    def update_user_data(self, user):
        validated_competencies = self.validated_data["competencies"]
        new_education_or_work = self.validated_data["education_or_work"]

        existing_competencies = Competencies.objects.filter(
            name__in=validated_competencies
        ).values_list("name", flat=True)

        missing_competencies = set(validated_competencies) - set(existing_competencies)

        if missing_competencies:
            Competencies.objects.bulk_create(
                [Competencies(name=name) for name in missing_competencies]
            )

        competence_objects = Competencies.objects.filter(
            name__in=validated_competencies
        )

        current_competencies_user = user.competencies.all()

        competencies_to_remove = current_competencies_user.exclude(
            name__in=validated_competencies
        )
        user.competencies.remove(*competencies_to_remove)
        user.competencies.add(*competence_objects)

        user.education_or_work = new_education_or_work
        user.save()


class UserDataPatchSerializer(Serializer):
    first_name = CharField(required=False)
    last_name = CharField(required=False)
    email = EmailField(required=False)
    avatar_link = URLField(required=False)
    birth_date = DateField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def validate_birth_date(self, value):
        if not value:
            return value

        today = date.today()
        if value > today:
            raise ValidationError(
                detail="Дата рождения не может быть в будущем.", code=400
            )

        return value

    def validate_email(self, value):
        if not value:
            return value

        instance = self.instance

        user_with_email = (
            Users.objects.filter(email=value).exclude(pk=instance.pk).first()
        )

        if user_with_email:
            raise ValidationError(
                detail={
                    "error": "Пользователь с такой электронной почтой уже существует."
                },
                code=400,
            )

        return value

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            current_value = getattr(instance, field)
            if current_value != value:
                setattr(instance, field, value)
        instance.save()
        return instance


class UserFullDataSerializer(ModelSerializer[Users]):
    competencies = CompetenciesSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "avatar_link",
            "education_or_work",
            "competencies",
        ]


class UserShortDataSerializer(ModelSerializer[Users]):
    class Meta:
        model = Users
        fields = [
            "first_name",
            "last_name",
            "avatar_link",
        ]


class UserParticipantSerializer(ModelSerializer[Users]):
    class Meta:
        model = Users
        fields = ["id", "first_name", "last_name", "email"]


class UserCompetenciesSerializer(ModelSerializer[Users]):
    competencies = CompetenciesSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = ["id", "first_name", "last_name", "email", "competencies"]
