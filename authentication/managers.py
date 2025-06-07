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
        birth_date,
        region_id,
    ):
        if not email:
            raise ValidationError("Пользователь должен иметь адрес электронной почты.")
        if not first_name:
            raise ValidationError("Пользователь должен иметь имя.")
        if not last_name:
            raise ValidationError("Пользователь должен иметь фамилию.")
        if not birth_date:
            raise ValidationError("Пользователь должен иметь дату рождения.")
        if not region_id:
            raise ValidationError("Пользователь должен иметь регион.")

    def create_user(
        self,
        email,
        first_name,
        last_name,
        birth_date,
        region_id,
        password=None,
        middle_name="",
    ):
        self._validate_required_fields(
            email=email,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            region_id=region_id,
        )
        self._validate_birth_date(birth_date=birth_date)

        email = self.normalize_email(email)

        if not middle_name:
            middle_name = self.model.middle_name.field.default

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            birth_date=birth_date,
            region_id=region_id,
        )

        user.set_password(raw_password=password)
        user.save()
        return user

    def create_superuser(
        self,
        email,
        first_name,
        last_name,
        middle_name,
        birth_date,
        region,
        password,
    ):
        if password is None:
            raise ValidationError("Суперпользователь должен иметь пароль")
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            birth_date=birth_date,
            password=password,
            region_id=region.id,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
