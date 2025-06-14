from block_user.models import UserBlock


def check_block_user(user_id: int) -> bool:
    return not UserBlock.objects.filter(user_id=user_id, blocked_by=True).exists()
