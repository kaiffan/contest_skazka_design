import datetime
from datetime import datetime
from typing import NoReturn

from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    SerializerMethodField,
    ValidationError,
    Serializer,
)
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import Users
from django.contrib.auth import authenticate

from authentication.validator import UserValidator


class RegistrationSerializer(ModelSerializer[Users]):
    class Meta:
        model = Users
        fields = [
            "first_name",
            "last_name",
            "email",
            "avatar_link",
            "birth_date",
            "password",
        ]

        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "birth_date": {"required": True},
            "password": {"required": True},
        }

    def validate_first_name(self, value):
        return UserValidator.validate_full_name(value=value)

    def validate_last_name(self, value):
        return UserValidator.validate_full_name(value=value)

    def validate_email(self, value):
        UserValidator.validate_email(email=value)
        if Users.objects.filter(email=value).exists():
            raise ValidationError(
                detail={"error": "A user with that email already exists."}, code=400
            )
        return value

    def validate_password(self, value):
        return UserValidator.validate_password(value=value)

    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise ValidationError(
                detail={"error": "Birth date cannot be in the future."}, code=400
            )
        return value

    def create(self, validated_data):
        return Users.objects.create_user(**validated_data)


class LoginSerializer(Serializer[Users]):
    email = CharField()
    password = CharField(write_only=True)
    tokens = SerializerMethodField()

    class Meta:
        model = Users
        fields = ["email", "password", "tokens"]

    def get_tokens(self, obj):
        user = Users.objects.get(email=obj.email)
        return {"refresh": user.tokens["refresh"], "access": user.tokens["access"]}

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise ValidationError(
                detail={"error": "An email address is required to log in."}, code=400
            )

        if not password:
            raise ValidationError(
                detail={"error": "A password is required to log in."}, code=400
            )

        user = authenticate(username=email, password=password)

        if not user:
            raise ValidationError(
                detail={"error": "A user with this email and password was not found."},
                code=404,
            )

        if not user.is_active:
            raise ValidationError(
                detail={"error": "This user is not currently activated."}, code=400
            )

        return user


class LogoutSerializer(Serializer[Users]):
    def validate(self, attrs) -> dict:
        token = self.context.get("refresh_token")
        if not token:
            raise serializers.ValidationError(
                {"refresh": ["Refresh token is missing in cookies."]}
            )

        self.token = token
        return attrs

    def save(self, **kwargs) -> NoReturn:
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except TokenError:
            raise AuthenticationFailed(detail={"error": "Refresh token is invalid"})


class PasswordResetSerializer(ModelSerializer[Users]):
    current_password = CharField(required=True)
    new_password = CharField(required=True)

    class Meta:
        model = Users
        fields = ["current_password", "new_password"]

    def validate(self, data):
        user = self.context.get("user")
        current_password = data.get("current_password")

        if not check_password(password=current_password, encoded=user.password):
            raise ValidationError(detail={"error": "Текущий пароль неверен."}, code=401)

        return data

    def update(self, instance, validated_data):
        new_password = validated_data.get("new_password")
        instance.set_password(new_password)
        instance.save()
        return instance
