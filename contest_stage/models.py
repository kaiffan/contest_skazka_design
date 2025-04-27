from django.db import models


class ContestStage(models.Model):
    name = models.CharField(name="name", max_length=255, unique=True, null=False)
    start_date = models.DateField(name="start_date", null=False)
    end_date = models.DateField(name="end_date", null=False)  # сравнить с контестом

    class Meta:
        db_table = "contest_stage"
