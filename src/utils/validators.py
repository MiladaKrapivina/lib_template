"""Функции проверки пользовательских и доменных данных."""

from datetime import date


class ValidationError(ValueError):
    """Исключение, возникающее при нарушении правил валидации."""


def require_text(value: str, field_name: str) -> str:
    """Проверяет, что текстовое поле заполнено, и возвращает очищенную строку."""
    cleaned = str(value).strip()
    if not cleaned:
        raise ValidationError(f"Поле '{field_name}' не может быть пустым")
    return cleaned


def validate_year(year: int) -> int:
    """Проверяет корректность года издания книги."""
    current_year = date.today().year
    if int(year) < 1450 or int(year) > current_year:
        raise ValidationError("Год издания должен быть в диапазоне от 1450 до текущего года")
    return int(year)


def validate_positive_int(value: int, field_name: str) -> int:
    """Проверяет, что значение является положительным целым числом."""
    number = int(value)
    if number < 1:
        raise ValidationError(f"Поле '{field_name}' должно быть положительным числом")
    return number


def validate_phone(phone: str) -> str:
    """Проверяет простую структуру телефонного номера читателя."""
    cleaned = require_text(phone, "телефон")
    digits = [char for char in cleaned if char.isdigit()]
    if len(digits) < 7:
        raise ValidationError("Телефон должен содержать минимум 7 цифр")
    return cleaned
