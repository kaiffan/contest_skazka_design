from django.db import models

from applications.enums import ApplicationStatus


class Applications(models.Model):
    name = models.CharField(name="name", max_length=255, null=False)
    annotation = models.CharField(name="annotation", max_length=255, null=False)
    link_to_work = models.CharField(
        name="link_to_work", max_length=255, null=False, default="asdasdasd"
    )
    status = models.CharField(
        name="status",
        max_length=255,
        choices=ApplicationStatus.choices(),
        default=ApplicationStatus.pending.value,
    )
    age_category = models.CharField(name="age_category", max_length=255, null=False)
    rejection_reason = models.CharField(
        name="rejection_reason", max_length=255, blank=True, null=True
    )

    nomination = models.ForeignKey(
        to="nomination.Nominations", on_delete=models.CASCADE
    )

    contest = models.ForeignKey(to="contests.Contest", on_delete=models.CASCADE)
    user = models.ForeignKey(to="authentication.Users", on_delete=models.CASCADE)

    work_rate = models.ManyToManyField(
        to="criteria.Criteria",
        through="work_rate.WorkRate",
        related_name="criteria_rate",
    )

    class Meta:
        db_table = "applications"
        unique_together = ("name", "contest", "nomination")
