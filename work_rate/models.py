from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class WorkRate(models.Model):
    criteria_id = models.ForeignKey(
        to="criteria.Criteria",
        on_delete=models.CASCADE,
    )

    application_id = models.ForeignKey(
        to="applications.Applications",
        on_delete=models.CASCADE,
    )

    rate = models.PositiveIntegerField(
        name="rate",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=False,
        blank=False,
    )

    class Meta:
        unique_together = ("criteria_id", "application_id")
        db_table = "work_rate"
