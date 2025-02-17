import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class NotEmptyValidator:
    """
    Валидатор для проверки, что поле не пустое.
    """

    def __call__(self, value: str):
        self.validate(value)

    def validate(self, value: str) -> None:
        if not value or value.strip() == "":
            raise ValidationError("Поле не может быть пустым.")


@deconstructible
class MinMaxLengthValidator:
    """
    Валидатор для проверки длины поля:
    - Минимум 2 символов
    - Максимум 255 символов
    """

    def __init__(self, min_length: int = 2, max_length: int = 255) -> None:
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value: str):
        self.validate(value)

    def validate(self, value: str) -> None:
        if len(value) < self.min_length:
            raise ValidationError(f"Пароль должен быть минимум {self.min_length} символов")

        if len(value) > self.max_length:
            raise ValidationError(f"Пароль должен быть максимум {self.max_length} символов")


@deconstructible
class OnlyLatinSymbolValidator:
    """
    Валидатор для проверки Только буквы латиницы :
    """

    LETTERS_PATTERN = re.compile(r"^[a-zA-Z ]$")

    def __call__(self, value: str):
        self.validate(value)

    def validate(self, value: str) -> None:
        if not self.LETTERS_PATTERN.match(value):
            raise ValidationError("Поле может содержать только буквы латиницы.")
