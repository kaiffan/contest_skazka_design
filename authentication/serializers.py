import datetime
from datetime import datetime
from typing import NoReturn

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    BooleanField,
    CharField,
    SerializerMethodField,
    ValidationError,
    Serializer,
)
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import Users
from django.contrib.auth import authenticate


class RegistrationSerializer(ModelSerializer[Users]):
    class Meta:
        model = Users
        fields = ["first_name", "last_name", "email", "birth_date", "password"]

    def create(self, validated_data):
        return Users.objects.create_user(**validated_data)

    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future.")
        return value


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
            raise ValidationError("An email address is required to log in.")

        if not password:
            raise ValidationError("A password is required to log in.")

        user = authenticate(username=email, password=password)

        if not user:
            raise ValidationError("A user with this email and password was not found.")

        if not user.is_active:
            raise ValidationError("This user is not currently activated.")

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
            raise AuthenticationFailed("Refresh token is invalid")
