from datetime import timedelta

from django.utils import timezone
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    ValidationError,
    IntegerField,
)
from authentication.models import Users
from block_user.models import UserBlock


class BlockUserSerializer(ModelSerializer[UserBlock]):
    user_id = IntegerField(write_only=True)
    blocked_until = DateTimeField(required=False)

    class Meta:
        model = UserBlock
        fields = ["user_id", "blocked_until"]

    def validate_user_id(self, value):
        try:
            user = Users.objects.get(id=value)
        except Users.DoesNotExist:
            raise ValidationError(detail={"error": "Пользователь не найден."}, code=404)
        return user.id

    def validate_blocked_until(self, value):
        if value is None:
            return timezone.now() + timedelta(days=7)  # значение по умолчанию

        if value < timezone.now():
            raise ValidationError(
                detail={"error": "Дата окончания блокировки не может быть в прошлом."},
                code=404,
            )

        return value

    def save(self):
        user_id = self.validated_data["user_id"]

        user_blocked = UserBlock.objects.get(user_id=user_id).is_blocked

        if user_blocked:
            raise ValidationError(
                detail={"error": "Этот пользователь уже заблокирован"}, code=404
            )

        blocked_until = self.validated_data.get("blocked_until")
        blocked_by_id = self.context.get("blocked_by_id")

        block, created = UserBlock.objects.update_or_create(
            user_id=user_id,
            defaults={
                "blocked_by_id": blocked_by_id,
                "blocked_until": blocked_until,
                "is_blocked": True,
            },
        )
        return block


class UnblockUserSerializer(ModelSerializer[UserBlock]):
    user_id = IntegerField(write_only=True)

    class Meta:
        model = UserBlock
        fields = ["user_id"]

    def validate_user_id(self, value):
        try:
            user = UserBlock.objects.get(user_id=value)
        except Users.DoesNotExist:
            raise ValidationError(
                detail={"error": "Заблокированный пользователь не найден в системе."},
                code=404,
            )
        return user.id

    def save(self):
        user_id = self.validated_data["user_id"]

        block = UserBlock.objects.get(id=user_id)
        block.is_blocked = False
        block.unblocked_at = timezone.now()
        block.save(update_fields=["unblocked_at", "is_blocked"])

        return block


class AllBlockUsersSerializer(ModelSerializer[UserBlock]):
    blocked_by_fio = SerializerMethodField()
    user_fio = SerializerMethodField()

    class Meta:
        model = UserBlock
        fields = [
            "user_id",
            "user_fio",
            "blocked_by_fio",
            "blocked_until",
            "is_blocked",
        ]

    def get_blocked_by_fio(self, instance):
        return instance.blocked_by.get_fio()

    def get_user_fio(self, instance):
        return instance.user.get_fio()
