"""Модель операции выдачи или возврата книги."""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Transaction:
    """Описывает выдачу книги читателю и сведения о возврате."""

    transaction_id: str
    book_id: str
    reader_id: str
    issue_date: str
    due_date: str
    return_date: Optional[str] = None
    fine: float = 0.0

    @property
    def is_active(self) -> bool:
        """Показывает, находится ли книга на руках у читателя."""
        return self.return_date is None

    def to_dict(self) -> dict:
        """Возвращает словарь для сохранения операции в JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Создаёт объект операции из словаря."""
        return cls(**data)
