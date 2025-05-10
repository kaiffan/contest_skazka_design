from django.db import models


class ContestsContestStage(models.Model):
    contest = models.ForeignKey(to="contests.Contest", on_delete=models.CASCADE)
    stage = models.ForeignKey(to="contest_stage.ContestStage", on_delete=models.CASCADE)

    start_date = models.DateField(name="start_date", null=False)
    end_date = models.DateField(name="end_date", null=False)

    class Meta:
        db_table = "contests_contest_stage"
        unique_together = ("contest", "stage")
