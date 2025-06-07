from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class WorkRate(models.Model):
    criteria = models.ForeignKey(
        to="criteria.Criteria",
        on_delete=models.CASCADE,
    )

    application = models.ForeignKey(
        to="applications.Applications",
        on_delete=models.CASCADE,
    )

    rate = models.PositiveIntegerField(
        name="rate",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=False,
        blank=False,
    )

    jury = models.ForeignKey(
        to="participants.Participant",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "work_rate"
        unique_together = ("criteria", "application", "jury")
