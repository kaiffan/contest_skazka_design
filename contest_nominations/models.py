from django.db import models


class ContestNominations(models.Model):
    contest = models.ForeignKey(to="contests.Contest", on_delete=models.CASCADE)
    nomination = models.ForeignKey(
        to="nomination.Nominations", on_delete=models.CASCADE
    )
    description = models.CharField(name="description", max_length=255, null=False)

    class Meta:
        db_table = "contest_nominations"
