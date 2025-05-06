from django.db import models

from contest_categories.models import ContestCategories
from criteria.models import Criteria
from nomination.models import Nominations
from regions.models import Region


class Contest(models.Model):
    title = models.CharField(name="title", max_length=255, unique=True, null=False)
    description = models.CharField(name="description", max_length=255, null=False)
    avatar = models.CharField(name="avatar", max_length=255, null=False, default=" ")
    link_to_rules = models.CharField(name="link_to_rules", max_length=255, null=False)
    organizer = models.CharField(name="organizer", max_length=255, null=False)
    is_draft = models.BooleanField(name="is_draft", null=False, default=True)
    is_deleted = models.BooleanField(name="is_deleted", null=False, default=False)
    is_published = models.BooleanField(name="is_published", null=False, default=False)

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
        to="criteria.Criteria", related_name="contest_criteria"
    )
    contest_stage = models.ManyToManyField(
        to="contest_stage.ContestStage",
        related_name="contest_stage",
    )

    class Meta:
        db_table = "contests"
