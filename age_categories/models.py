from django.db import models


class AgeCategories(models.Model):
    name = models.CharField(name="name", max_length=255, null=False, unique=True)
    start_age = models.PositiveIntegerField(name="start_age", null=False, default=0)
    end_age = models.PositiveIntegerField(name="end_age", null=False, default=0)

    class Meta:
        db_table = "age_categories"
