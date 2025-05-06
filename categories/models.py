from django.db import models

from contests.models import Contest
from nomination.models import Nominations


class Categories(models.Model):
    age_category = models.ForeignKey(
        to="age_categories.AgeCategories", on_delete=models.CASCADE
    )
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
        unique_together = ("age_category", "contest", "nominations")
