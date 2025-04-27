from rest_framework.fields import ListField, IntegerField
from rest_framework.serializers import Serializer

from participants.enums import ParticipantRole
from participants.models import Participant


class JuryParticipantSerializer(Serializer):
    jury_ids = ListField(
        child=IntegerField(),
        allow_empty=False,
        allow_null=False,
        error_messages={
            "required": "Поле user_ids обязательно.",
            "not_a_list": "Значение должно быть списком.",
            "empty": "Список не может быть пустым.",
        },
    )

    def update_list_jury_in_contest(self) -> dict[str, list[str]]:
        validated_jury_ids = self.validated_data["jury_ids"]
        contest_id = self.context.get("contest_id")

        existing_jury = Participant.objects.filter(
            user_id__in=validated_jury_ids,
            contest_id=contest_id,
            role=ParticipantRole.jury.value,
        ).values_list("user_id", flat=True)

        missing_jury = set(validated_jury_ids) - set(existing_jury)

        if missing_jury:
            Participant.objects.bulk_create(
                [
                    Participant(
                        contest_id=contest_id,
                        user_id=user_id,
                        role=ParticipantRole.jury.value,
                    )
                    for user_id in missing_jury
                ]
            )

        jury_to_remove = Participant.objects.filter(
            contest_id=contest_id,
            role=ParticipantRole.jury.value,
        ).exclude(user_id__in=validated_jury_ids)

        if jury_to_remove.exists():
            jury_to_remove.delete()

        return {
            "added_jury": list(missing_jury),
            "removed_jury": list(jury_to_remove.values_list("user_id", flat=True)),
        }
