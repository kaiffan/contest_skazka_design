from rest_framework.permissions import BasePermission

from participants.enums import ParticipantRole

from participants.utils import check_contest_role_permission


class IsContestOwner(BasePermission):
    def has_permission(self, request, view) -> bool:
        return check_contest_role_permission(
            contest_id=request.contest_id,
            user_id=request.user.id,
            role=ParticipantRole.owner.value,
        )


class IsContestJury(BasePermission):
    def has_permission(self, request, view) -> bool:
        return check_contest_role_permission(
            contest_id=request.contest_id,
            user_id=request.user.id,
            role=ParticipantRole.jury,
        )


class IsContestMember(BasePermission):
    def has_permission(self, request, view) -> bool:
        return check_contest_role_permission(
            contest_id=request.contest_id,
            user_id=request.user.id,
            role=ParticipantRole.member,
        )


class IsOrgCommittee(BasePermission):
    def has_permission(self, request, view) -> bool:
        return check_contest_role_permission(
            contest_id=request.contest_id,
            user_id=request.user.id,
            role=ParticipantRole.org_committee,
        )
