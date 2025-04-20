from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models

from authentication.managers import UsersManager


class Users(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(name="first_name", max_length=25, null=False)
    last_name = models.CharField(name="last_name", max_length=25, null=False)
    email = models.EmailField(name="email", max_length=255, unique=True, null=False)
    birth_date = models.DateField(name="birth_date", null=False)
    password = models.CharField(name="password", max_length=255, default="", null=False)
    registration_date = models.DateTimeField(
        name="registration_date", auto_now_add=True, null=False
    )
    avatar = models.CharField(
        name="avatar",
        max_length=255,
        null=False,
        default="http://localhost:3000/static/images/default_avatar.jpg",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsersManager()

    class Meta:
        db_table = "users"

    @property
    def tokens(self) -> dict[str, str]:
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
