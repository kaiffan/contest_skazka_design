import uuid
from hmac import new
from string import ascii_letters, digits
from secrets import choice
from datetime import timedelta
from django.utils import timezone
from django.db import models
from contest_backend import settings
from hashlib import sha512


class EmailConfirmationLogin(models.Model):
    user = models.ForeignKey(to="authentication.Users", on_delete=models.CASCADE)
    code_hash = models.CharField(
        max_length=255, unique=True, db_index=True, editable=False
    )
    session_id = models.CharField(name="session_id", max_length=255, editable=False, db_index=True)
    attempt_number = models.PositiveIntegerField(name="attempt_number", editable=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls) -> tuple[str, str]:
        code = "".join(choice(ascii_letters + digits) for _ in range(8))
        code_hash = cls.hash_code(code)
        return code, code_hash

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=10)

    @staticmethod
    def hash_code(code: str) -> str:
        key = getattr(settings, "CODE_CONFIRMATION_SALT", None).encode("utf-8")
        if not key:
            raise ValueError("CODE_CONFIRMATION_SALT must be set in settings")

        code_bytes = code.encode("utf-8")
        return new(key=key, msg=code_bytes, digestmod=sha512).hexdigest()

    @classmethod
    def generate_session_id(cls) -> str:
        return uuid.uuid4().hex

    class Meta:
        db_table = "email_confirmation"
