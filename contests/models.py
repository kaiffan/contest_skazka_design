from django.db import models

from contest_categories.models import ContestCategories
from criterias.models import Criteria
from nomination.models import Nominations
from regions.models import Region


class Contest(models.Model):
    title = models.CharField(name="title", max_length=255, unique=True, null=False)
    description = models.CharField(name="description", max_length=255, null=False)
    link_to_rules = models.CharField(name="link_to_rules", max_length=255, null=False)
    date_start = models.DateField(name="date_start", null=False)
    date_end = models.DateField(name="date_end", null=False)
    organizer = models.CharField(name="organizer", max_length=255, null=False)
    is_draft = models.BooleanField(name="is_draft", null=False, default=False)

    contest_categories = models.ForeignKey(
        to="contest_categories.ContestCategories", on_delete=models.CASCADE
    )
    region = models.ForeignKey(to="regions.Region", on_delete=models.CASCADE)

    participants = models.ManyToManyField(
        to="authentication.Users",
        through="participants.Participant",
        related_name="contest_participants",
    )
    categories = models.ManyToManyField(
        to="nomination.Nominations",
        through="categories.Categories",
        related_name="contest_nominations",
    )
    criteria = models.ManyToManyField(
        to="criterias.Criteria", related_name="contest_criteria"
    )

    class Meta:
        db_table = "contests"
