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
    prizes = models.TextField(name="prizes", null=False)
    contacts_for_participants = models.CharField(
        name="contacts_for_participants", max_length=255, null=False
    )
    is_draft = models.BooleanField(name="is_draft", null=False, default=True)
    is_deleted = models.BooleanField(name="is_deleted", null=False, default=False)
    is_published = models.BooleanField(name="is_published", null=False, default=False)

    contest_category = models.ForeignKey(
        to="contest_categories.ContestCategories", on_delete=models.CASCADE
    )
    region = models.ForeignKey(to="regions.Region", on_delete=models.CASCADE)

    participants = models.ManyToManyField(
        to="authentication.Users",
        through="participants.Participant",
        related_name="contest_participants",
    )
    age_category = models.ManyToManyField(
        to="age_categories.AgeCategories", related_name="contest_age_categories"
    )
    nominations = models.ManyToManyField(
        to="nomination.Nominations",
        through="contest_nominations.ContestNominations",
        related_name="contest_nominations",
    )
    criteria = models.ManyToManyField(
        to="criteria.Criteria",
        through="contest_criteria.ContestCriteria",
        related_name="contest_criteria",
    )
    contest_stage = models.ManyToManyField(
        to="contest_stage.ContestStage",
        through="contests_contest_stage.ContestsContestStage",
        through_fields=("contest", "stage"),
        related_name="contest_stages",
    )
    file_constraint = models.ManyToManyField(
        to="file_constraints.FileConstraint",
        through="contest_file_constraints.ContestFileConstraints",
        related_name="contest_file_constraints",
    )
    winner_list = models.ManyToManyField(
        to="applications.Applications",
        through="winners.Winners",
        related_name="contest_winners",
    )

    class Meta:
        db_table = "contests"
