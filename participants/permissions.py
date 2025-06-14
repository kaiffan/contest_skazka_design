from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from participants.enums import ParticipantRole
from participants.models import Participant


class BaseContestRolePermission(BasePermission):
    role = None
    message = "Недостаточно прав для выполнения действия."

    def has_permission(self, request, view):
        contest_id = getattr(request, 'contest_id', None)
        user = request.user

        if not contest_id:
            raise PermissionDenied("Контекст конкурса не указан.")

        if not Participant.objects.filter(
            contest_id=contest_id,
            user_id=user.id,
            role=self.role.value,
        ).exists():
            raise PermissionDenied(f"Для этого действия требуется роль: {self.role.label}")

        return True


class IsContestOwnerPermission(BaseContestRolePermission):
    role = ParticipantRole.owner


class IsContestJuryPermission(BasePermission):
    role = ParticipantRole.jury


class IsContestMemberPermission(BasePermission):
    role = ParticipantRole.member


class IsOrgCommitteePermission(BasePermission):
    role = ParticipantRole.org_committee
