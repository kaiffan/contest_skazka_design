from django.db import models

from authentication.models import Users
from participants.models import Participant


class Contest(models.Model):
    title = models.CharField(name="title", max_length=255, unique=True, null=False)
    description = models.CharField(name="description", max_length=255, null=False)
    link_to_rules = models.CharField(name="link_to_rules", max_length=255, null=False)
    date_start = models.DateField(name="date_start", null=False)
    date_end = models.DateField(name="date_end", null=False)

    participants = models.ManyToManyField(
        to=Users, through=Participant, related_name="contest_participants"
    )

    class Meta:
        db_table = "contests"
