from enum import Enum


class ApplicationStatus(Enum):
    accepted = "ACCEPTED"
    pending = "PENDING"
    rejected = "REJECTED"

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
