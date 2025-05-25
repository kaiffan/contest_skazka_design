from django.db import models


class Criteria(models.Model):
    name = models.CharField(name="name", max_length=255, null=False, unique=True, db_index=True)

    class Meta:
        db_table = "criteria"
        indexes = [
            models.Index(fields=["name"]),
        ]
