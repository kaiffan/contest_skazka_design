from datetime import date

from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError


class UsersManager(BaseUserManager):
    def _validate_birth_date(self, birth_date):
        if birth_date > date.today():
            raise ValidationError("Дата рождения не может быть в будущем.")

    def _validate_required_fields(
        self,
        email,
        first_name,
        last_name,
        birth_date
    ):
        if not email:
            raise ValidationError("Пользователь должен иметь адрес электронной почты.")
        if not first_name:
            raise ValidationError("Пользователь должен иметь имя.")
        if not last_name:
            raise ValidationError("Пользователь должен иметь фамилию.")
        if not birth_date:
            raise ValidationError("Пользователь должен иметь дату рождения.")

    def create_user(
        self,
        email,
        first_name,
        last_name,
        birth_date,
        password=None,
    ):
        self._validate_required_fields(
            email=email,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date
        )
        self._validate_birth_date(birth_date=birth_date)

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name[:1] + ".",
            birth_date=birth_date,
        )

        user.set_password(raw_password=password)
        user.save()
        return user

    def create_superuser(
        self,
        email,
        first_name,
        last_name,
        birth_date,
        password,
    ):
        if password is None:
            raise ValidationError("Суперпользователь должен иметь пароль")
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            password=password
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
