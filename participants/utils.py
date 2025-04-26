from config.logger import logger
from participants.enums import ParticipantRole
from participants.models import Participant


def check_contest_role_permission(
    contest_id: int, user_id: int, role: ParticipantRole
) -> bool:
    if not contest_id:
        return False
    is_role = Participant.objects.filter(
        contest_id=contest_id,
        user_id=user_id,
        role=role,
    ).exists()

    if not is_role:
        logger.warning(msg=f"Пользователь {user_id} не имеет роли {role}.")

    return is_role
