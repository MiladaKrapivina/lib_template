"""Модель читателя библиотеки."""

from dataclasses import dataclass, asdict


@dataclass
class Reader:
    """Хранит регистрационные и контактные данные читателя."""

    reader_id: str
    full_name: str
    phone: str
    registration_date: str

    def to_dict(self) -> dict:
        """Возвращает словарь для сохранения читателя в JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Reader":
        """Создаёт объект читателя из словаря."""
        return cls(**data)
