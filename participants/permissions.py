from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from participants.enums import ParticipantRole
from participants.models import Participant


class BaseContestRolePermission(BasePermission):
    role = None
    message = "Недостаточно прав для выполнения действия."

    def has_permission(self, request, view):
        contest_id = request.contest_id
        user = request.user

        if not contest_id:
            raise PermissionDenied("Контекст конкурса не указан.")

        if not Participant.objects.filter(
            contest_id=contest_id,
            user_id=user.id,
            role=self.role.value,
        ).exists():
            raise PermissionDenied(
                f"Для этого действия требуется роль: {self.role.value}"
            )

        return True


class IsContestOwnerPermission(BaseContestRolePermission):
    role = ParticipantRole.owner


class IsContestJuryPermission(BaseContestRolePermission):
    role = ParticipantRole.jury


class IsContestMemberPermission(BaseContestRolePermission):
    role = ParticipantRole.member


class IsOrgCommitteePermission(BaseContestRolePermission):
    role = ParticipantRole.org_committee
