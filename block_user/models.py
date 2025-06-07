from django.db import models
from django.utils import timezone

class UserBlock(models.Model):
    user = models.ForeignKey(
        to="authentication.Users",
        on_delete=models.CASCADE,
        related_name="user_blocks",
        verbose_name="Заблокированный пользователь"
    )
    blocked_by = models.ForeignKey(
        to="authentication.Users",
        on_delete=models.CASCADE,
        related_name="user_blocks_created",
        verbose_name="Кем заблокирован"
    )
    blocked_until = models.DateTimeField(
        null=False,
        verbose_name="Заблокирован до"
    )
    unblocked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Разблокирован в"
    )
    is_blocked = models.BooleanField(
        default=True,
        verbose_name="Статус блокировки"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_blocks"

    @property
    def block_status(self) -> bool:
        if not self.is_blocked:
            return False
        if self.blocked_until and timezone.now() < self.blocked_until:
            return False
        return True