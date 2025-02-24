import re

from django.core.exceptions import ValidationError

from pydantic import BaseModel, field_validator, ValidationInfo


class NotEmptyValidator:
    """
    Валидатор для проверки, что поле не пустое.
    """

    def __call__(self, value: str):
        self.validate(value)

    def validate(self, value: str) -> None:
        if not value or value.strip() == "":
            raise ValidationError("Поле не может быть пустым.")


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
            raise ValidationError(f"Длина поля должна быть минимум {self.min_length}")

        if len(value) > self.max_length:
            raise ValidationError(f"Длина поля должна быть максимум {self.max_length}")


class OnlyLatinSymbolValidator:
    """
    Валидатор для проверки Только буквы латиницы :
    """

    LETTERS_PATTERN = re.compile(r"^[a-zA-Z ]+$")

    def __call__(self, value: str):
        self.validate(value)

    def validate(self, value: str) -> None:
        if not self.LETTERS_PATTERN.match(value):
            raise ValidationError("Поле может содержать только буквы латиницы и пробелы")


class LotteryUpdateSchema(BaseModel):
    name: str
    description: str
    is_active: bool

    class Config:
        from_attributes = True

    @field_validator("name")
    def validate_name(cls, value: str, info: ValidationInfo) -> str:
        try:
            NotEmptyValidator().validate(value)
            MinMaxLengthValidator(min_length=3, max_length=255).validate(value)
            OnlyLatinSymbolValidator().validate(value)
        except ValidationError as e:
            raise ValueError(e)
        return value

    @field_validator("description")
    def validate_description(cls, value: str, info: ValidationInfo) -> str:
        if value:
            try:
                MinMaxLengthValidator(min_length=3, max_length=255).validate(value)
            except ValidationError as e:
                raise ValueError(e)
        return value
