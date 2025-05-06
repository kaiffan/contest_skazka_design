from enum import Enum


class UserRole(Enum):
    user: str = "USER"
    admin: str = "ADMIN"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
