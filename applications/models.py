from django.db import models

from authentication.models import Users
from contests.models import Contest

from applications.enums import ApplicationStatus


class Applications(models.Model):
    name = models.CharField(name="name", max_length=255, null=False)
    annotation = models.CharField(name="annotation", max_length=255, null=False)
    link_to_work = models.CharField(name="link_to_work", max_length=255, null=False)
    status = models.CharField(
        null=False,
        name="status",
        max_length=255,
        choices=ApplicationStatus.choices(),
        default=ApplicationStatus.pending.value,
    )

    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(to=Users, on_delete=models.CASCADE)

    class Meta:
        db_table = "applications"
