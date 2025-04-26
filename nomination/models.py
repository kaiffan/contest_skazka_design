from django.db import models


class Nominations(models.Model):
    name = models.CharField(name="name", max_length=255, null=False, unique=True)
    description = models.CharField(name="description", max_length=255, null=False)

    class Meta:
        db_table = "nominations"
