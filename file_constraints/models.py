from django.db import models


class FileConstraint(models.Model):
    name = models.CharField(max_length=255, unique=True, editable=False)
    file_formats = models.TextField(editable=False)

    class Meta:
        db_table = "file_constraint"
