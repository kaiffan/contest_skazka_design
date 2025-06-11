from rest_framework.permissions import BasePermission

from block_user.utils import check_block_user


class IsNotBlockUserPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        return check_block_user(user_id=request.user.id)
