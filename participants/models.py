from django.db import models

from authentication.models import Users
from contests.models import Contest
from participants.enums import ParticipantRole


class Participant(models.Model):
    user = models.ForeignKey(to="authentication.Users", on_delete=models.CASCADE)
    contest = models.ForeignKey(to="contests.Contest", on_delete=models.CASCADE)

    role = models.CharField(
        name="role",
        max_length=255,
        null=False,
        choices=ParticipantRole.choices,
        default=ParticipantRole.member.value,
    )

    class Meta:
        db_table = "participants"
        unique_together = ("user", "contest")
