"""Модель книги библиотечного фонда."""

from dataclasses import dataclass, asdict


@dataclass
class Book:
    """Описывает книгу и количество её экземпляров в библиотеке."""

    book_id: str
    title: str
    author: str
    year: int
    genre: str
    copies: int

    def to_dict(self) -> dict:
        """Возвращает словарь для сохранения книги в JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Создаёт объект книги из словаря."""
        return cls(**data)
