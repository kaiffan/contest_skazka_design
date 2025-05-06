from rest_framework.permissions import BasePermission

from authentication.enums import UserRole


class IsAdminSystemPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_role == UserRole.admin.value:
            return True
        return False
