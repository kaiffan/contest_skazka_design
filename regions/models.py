from django.db import models


class Region(models.Model):
    name = models.CharField(name="name", max_length=255, null=False, unique=True)

    class Meta:
        db_table = "region"
