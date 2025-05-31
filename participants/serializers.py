from rest_framework.fields import ListField, IntegerField, SerializerMethodField
from rest_framework.serializers import Serializer, ModelSerializer

from participants.enums import ParticipantRole
from participants.models import Participant
from users.serializers import UserParticipantSerializer


def update_participant_in_contest_with_change_role(
    participant_ids, contest_id, role: ParticipantRole
) -> dict[str, list[str]]:
    existing_participants_by_role = Participant.objects.filter(
        user_id__in=participant_ids,
        contest_id=contest_id,
        role=role,
    ).values_list("user_id", flat=True)

    missing_participants = set(participant_ids) - set(existing_participants_by_role)

    if missing_participants:
        Participant.objects.bulk_create(objs=[
                Participant(
                    contest_id=contest_id,
                    user_id=user_id,
                    role=role,
                )
                for user_id in missing_participants
            ]
        )

    participants_to_remove = Participant.objects.filter(
        contest_id=contest_id,
        role=role,
    ).exclude(user_id__in=participant_ids)

    participants_to_remove_ids: list[int] = [participant.user.id for participant in participants_to_remove]

    if participants_to_remove.exists():
        participants_to_remove.delete()

    return {
        f"added_{role}": list(missing_participants),
        f"removed_{role}": participants_to_remove_ids,
    }


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
        return update_participant_in_contest_with_change_role(
            participant_ids=self.validated_data["jury_ids"],
            contest_id=self.context.get("contest_id"),
            role=ParticipantRole.jury.value,
        )


class OrgCommitteeParticipantSerializer(Serializer):
    org_committee_ids = ListField(
        child=IntegerField(),
        allow_empty=False,
        allow_null=False,
        error_messages={
            "required": "Поле user_ids обязательно.",
            "not_a_list": "Значение должно быть списком.",
            "empty": "Список не может быть пустым.",
        },
    )

    def update_list_org_committee_in_contest(self) -> dict[str, list[str]]:
        return update_participant_in_contest_with_change_role(
            participant_ids=self.validated_data["org_committee_ids"],
            contest_id=self.context.get("contest_id"),
            role=ParticipantRole.org_committee.value,
        )


class ParticipantSerializer(ModelSerializer[Participant]):
    class Meta:
        model = Participant
        fields = "__all__"


class PartisipantContestSerializer(ModelSerializer[Participant]):
    user = UserParticipantSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = [
            "user",
            "role"
        ]