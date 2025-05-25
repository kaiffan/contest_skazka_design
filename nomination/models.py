from django.db import models

# реализовать поиск по имени


class Nominations(models.Model):
    name = models.CharField(name="name", max_length=255, null=False, unique=True, db_index=True)

    class Meta:
        db_table = "nominations"
        indexes = [
            models.Index(fields=["name"]),
        ]
