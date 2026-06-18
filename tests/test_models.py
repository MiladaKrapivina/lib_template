"""Тесты моделей данных библиотеки."""

import unittest

from src.models.book import Book
from src.models.transaction import Transaction


class ModelTests(unittest.TestCase):
    """Проверяет сериализацию и свойства моделей."""

    def test_book_roundtrip(self) -> None:
        """Книга корректно преобразуется в словарь и обратно."""
        book = Book("1", "1984", "George Orwell", 1949, "Dystopia", 3)
        self.assertEqual(Book.from_dict(book.to_dict()), book)

    def test_transaction_active_property(self) -> None:
        """Операция без даты возврата считается активной."""
        tx = Transaction("t1", "b1", "r1", "2026-01-01", "2026-01-15")
        self.assertTrue(tx.is_active)
        tx.return_date = "2026-01-10"
        self.assertFalse(tx.is_active)


if __name__ == "__main__":
    unittest.main()
