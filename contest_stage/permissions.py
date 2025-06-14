from typing import Any

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from contests.models import Contest
from contests.utils import get_current_contest_stage


class BaseStagePermission(permissions.BasePermission):
    allowed_stage = None
    message = "Это действие доступно только на определённой стадии."

    def get_contest_id(self, request):
        contest_id = request.contest_id
        if not contest_id:
            raise PermissionDenied(detail="Not contest_id in header")

        return contest_id

    def has_permission(self, request, view):
        contest_id = self.get_contest_id(request)

        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return False

        current_stage: dict[str, Any] = get_current_contest_stage(contest_id=contest.id)

        if current_stage["name"] != self.allowed_stage:
            return False

        return True


class CanSubmitApplicationPermission(BaseStagePermission):
    allowed_stage = "Сбор заявок"
    message = "Заявку можно отправить только на стадии: 'Сбор заявок'."


class CanCheckWorksPermission(BaseStagePermission):
    allowed_stage = "Оценка работы"
    message = "Проверка работ возможна только на стадии: 'Оценка работы'."


class CanFinalizeResultsPermission(BaseStagePermission):
    allowed_stage = "Подведение итогов"
    message = "Итоги можно подводить только на стадии: 'Подведение итогов'."
