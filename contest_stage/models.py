from django.db import models


class ContestStage(models.Model):
    name = models.CharField(name="name", max_length=255, null=False)

    class Meta:
        db_table = "contest_stage"
