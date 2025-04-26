from django.db import models

from contests.models import Contest
from nomination.models import Nominations


class Categories(models.Model):
    name = models.CharField(name="name", max_length=255, null=False, unique=True)
    start_age = models.PositiveIntegerField(name="start_age", null=False, default=0)
    end_age = models.PositiveIntegerField(name="end_age", null=False, default=0)

    contest = models.ForeignKey(
        to="contests.Contest", on_delete=models.CASCADE, related_name="category_set"
    )
    nominations = models.ForeignKey(
        to="nomination.Nominations",
        on_delete=models.CASCADE,
        related_name="category_set",
    )

    class Meta:
        db_table = "categories"
