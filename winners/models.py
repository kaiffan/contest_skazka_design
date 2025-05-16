from django.db import models


class Winners(models.Model):
    contest = models.ForeignKey(to="contests.Contest", on_delete=models.CASCADE)
    application = models.ForeignKey(
        to="applications.Applications", on_delete=models.CASCADE
    )
    sum_rate = models.PositiveIntegerField(name="sum rate", null=False, default=0)
    place = models.PositiveIntegerField(name="place", null=False, default=0)

    class Meta:
        db_table = "winners"
        unique_together = ("contest", "application")
