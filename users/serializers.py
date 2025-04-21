from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField, CharField
from rest_framework.serializers import Serializer, ModelSerializer

from authentication.models import Users
from competencies.models import Competencies
from competencies.serializers import CompetenciesSerializer
from regions.models import Region
from regions.serializers import RegionSerializer


class ContestDataUpdateSerializer(Serializer):
    competencies = ListField(child=CharField(), required=True)
    education_or_work = CharField(max_length=255, required=True)

    def validate_competencies(self, value):
        existing_competences = set(
            Competencies.objects.filter(name__in=value).values_list("name", flat=True)
        )
        if len(existing_competences) != len(value):
            invalid_competences = set(value) - existing_competences
            raise ValidationError(
                f"Недопустимые компетенции: {', '.join(invalid_competences)}"
            )
        return value

    def update_user_data(self, user):
        validated_competencies = self.validated_data["competencies"]
        new_education_or_work = self.validated_data["education_or_work"]

        existing_competencies = set(
            Competencies.objects.filter(name__in=validated_competencies).values_list(
                "name", flat=True
            )
        )

        missing_competencies = set(validated_competencies) - existing_competencies

        if missing_competencies:
            Competencies.objects.bulk_create(
                [Competencies(name=name) for name in missing_competencies]
            )

        competence_objects = Competencies.objects.filter(
            name__in=validated_competencies
        )

        user.competencies.clear()
        user.competencies.add(*competence_objects)

        user.education_or_work = new_education_or_work
        user.save()


class UserDataPatchSerializer(ModelSerializer[Users]):
    class Meta:
        model = Users
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "phone_number",
            "email",
            "avatar_link",
            "birth_date",
            "region_id",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "middle_name": {"required": False},
            "phone_number": {"required": False},
            "email": {"required": False},
            "avatar_link": {"required": False},
            "birth_date": {"required": False},
            "region_id": {"required": False},
        }

    def validate_region_id(self, value):
        if not Region.objects.filter(id=value).exists():
            raise ValidationError("Регион с таким ID не существует.")
        return value

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class UserFullDataSerializer(ModelSerializer[Users]):
    region = RegionSerializer(read_only=True)
    competencies = CompetenciesSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "phone_number",
            "email",
            "birth_date",
            "avatar_link",
            "education_or_work",
            "region",
            "competencies",
        ]


class AllUsersShortDataSerializer(ModelSerializer[Users]):
    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "phone_number",
        ]
