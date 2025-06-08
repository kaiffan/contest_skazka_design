from typing import NoReturn

from rest_framework.exceptions import ValidationError
from re import compile, search


class UserValidator:
    """
    Вспомогательный класс для валидации ФИО
    """

    @staticmethod
    def validate_full_name(value: str) -> str:
        """
        Валидация полного имени (например: имя, фамилия, отчество).
        Допускаются только русские буквы (включая Ё/ё).

        :param value: строка с полным именем
        :raises ValidationError: если строка пустая или содержит недопустимые символы
        :return: исходное значение (если валидно)
        """
        if not value:
            raise ValidationError(
                detail={"error": "Имя, фамилия, отчество не может быть пустым"},
                code=400,
            )

        value_not_space = value.strip()

        pattern = compile(pattern=r"^[а-яА-ЯёЁ]+$")
        if not pattern.match(string=value_not_space):
            raise ValidationError(
                detail={
                    "error": "Поле может содержать только буквы, пробелы, дефисы и апострофы."
                },
                code=400,
            )
        return value

    @staticmethod
    def validate_email(email: str) -> NoReturn:
        """
        Валидация электронной почты. Допускается только формат: example@domain.region

        :param email: строка с email-адресом
        :raises ValidationError: если почта пустая или не соответствует шаблону
        """
        if not email:
            raise ValidationError(
                detail={"error": "Почта не может быть пустой"}, code=400
            )

        email = email.strip()
        pattern = compile(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")

        if not pattern.match(string=email):
            raise ValidationError(
                detail={"error": "Почта не соответствует формату - example@email.com"},
                code=400,
            )

    @staticmethod
    def validate_password(value: str) -> str:
        """
        Валидация пароля по расширенным требованиям безопасности:
        - Минимум 10 символов
        - Хотя бы одна заглавная, строчная, цифра и спецсимвол
        - Запрещены последовательности 3 и более строчных, заглавных букв или цифр подряд

        :param value: строка с паролем
        :raises ValidationError: если нарушено хотя бы одно из условий
        :return: исходное значение (если валидно)
        """
        if len(value) < 10:
            raise ValidationError(
                detail={"error": "Пароль должен содержать минимум 10 символов."},
                code=400,
            )

        if len(set(value)) < 5:
            raise ValidationError(
                detail={
                    "error": "Пароль должен содержать хотя бы 5 уникальных символов."
                },
                code=400,
            )

        if not search(pattern=r"[A-Z]", string=value):
            raise ValidationError(
                detail={
                    "error": "Пароль должен содержать хотя бы одну заглавную букву."
                },
                code=400,
            )

        if not search(pattern=r"[a-z]", string=value):
            raise ValidationError(
                detail={
                    "error": "Пароль должен содержать хотя бы одну строчную букву."
                },
                code=400,
            )
        if not search(pattern=r"[0-9]", string=value):
            raise ValidationError(
                detail={"error": "Пароль должен содержать хотя бы одну цифру."},
                code=400,
            )

        if not search(pattern=r"[!@#$%^&*(),.?\":{}|<>]", string=value):
            raise ValidationError(
                detail={
                    "error": "Пароль должен содержать хотя бы один специальный символ."
                },
                code=400,
            )

        rules: list[tuple[str, str]] = [
            (r"[a-z]{3,}", "строчных букв"),
            (r"[A-Z]{3,}", "заглавных букв"),
            (r"\d{3,}", "цифр"),
        ]

        for pattern, description in rules:
            if search(pattern=pattern, string=value):
                raise ValidationError(
                    detail={
                        "error": f"Пароль не должен содержать более трёх {description} подряд."
                    },
                    code=400,
                )

        return value
