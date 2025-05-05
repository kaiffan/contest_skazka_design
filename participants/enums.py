from enum import Enum


class ParticipantRole(Enum):
    org_committee: str = "ORG_COMMITTEE"
    member: str = "MEMBER"
    owner: str = "OWNER"
    jury: str = "JURY"

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]
