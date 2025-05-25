from django.db import models


class ContestCriteria(models.Model):
    contest = models.ForeignKey(to="contests.Contest", on_delete=models.CASCADE)
    criteria = models.ForeignKey(to="criteria.Criteria", on_delete=models.CASCADE)
    description = models.CharField(name="description", max_length=255, null=False)
    max_points = models.PositiveIntegerField(name="max_points", null=False)
    min_points = models.PositiveIntegerField(name="min_points", null=False)

    class Meta:
        db_table = "contest_criteria"
