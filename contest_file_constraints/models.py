from django.db import models


class ContestFileConstraints(models.Model):
    contest = models.ForeignKey(to="contests.Contest", on_delete=models.CASCADE)

    file_constraints = models.ForeignKey(
        to="file_constraints.FileConstraint", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "contest_file_constraints"
        unique_together = ("contest", "file_constraints")
