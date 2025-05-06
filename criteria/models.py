from django.db import models


class Criteria(models.Model):
    name = models.CharField(name="name", max_length=255, unique=True, null=False)
    description = models.CharField(name="description", max_length=255, null=False)
    max_points = models.PositiveIntegerField(name="max_points", null=False)
    min_points = models.PositiveIntegerField(name="min_points", null=False)

    class Meta:
        db_table = "criteria"
