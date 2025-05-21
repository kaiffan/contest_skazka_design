from rest_framework.permissions import BasePermission

from authentication.enums import UserRole


class IsAdminSystemPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.user_role == UserRole.admin.value:
            return False
        return True
