"""Тесты бизнес-логики библиотечного сервиса."""

import tempfile
import unittest
from datetime import date, timedelta

from src.services.data_manager import DataManager
from src.services.library_service import LibraryError, LibraryService


class LibraryServiceTests(unittest.TestCase):
    """Проверяет ключевые сценарии управления фондом."""

    def setUp(self) -> None:
        """Создаёт изолированное временное хранилище для каждого теста."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = LibraryService(DataManager(self.temp_dir.name), fine_per_day=5.0)

    def tearDown(self) -> None:
        """Удаляет временное хранилище после теста."""
        self.temp_dir.cleanup()

    def test_issue_and_return_with_fine(self) -> None:
        """Сервис выдаёт книгу и начисляет штраф при позднем возврате."""
        self.service.add_book("b1", "Clean Code", "Robert Martin", 2008, "Programming", 1)
        self.service.register_reader("r1", "Ivan Petrov", "+7 900 000 00 00")
        tx = self.service.issue_book("b1", "r1", days=1)
        self.assertEqual(self.service.available_copies("b1"), 0)
        returned = self.service.return_book(tx.transaction_id, (date.today() + timedelta(days=3)).isoformat())
        self.assertEqual(returned.fine, 10.0)
        self.assertEqual(self.service.available_copies("b1"), 1)

    def test_cannot_delete_book_with_active_issue(self) -> None:
        """Книгу с активной выдачей нельзя удалить."""
        self.service.add_book("b1", "Dune", "Frank Herbert", 1965, "Sci-Fi", 1)
        self.service.register_reader("r1", "Anna Smirnova", "+7 900 111 11 11")
        self.service.issue_book("b1", "r1")
        with self.assertRaises(LibraryError):
            self.service.delete_book("b1")

    def test_search_books_by_query_and_genre(self) -> None:
        """Поиск находит книги по автору и фильтрует по жанру."""
        self.service.add_book("b1", "Dune", "Frank Herbert", 1965, "Sci-Fi", 2)
        self.service.add_book("b2", "Python 101", "Michael Driscoll", 2020, "Programming", 1)
        result = self.service.search_books("frank", "Sci-Fi")
        self.assertEqual([book.book_id for book in result], ["b1"])


if __name__ == "__main__":
    unittest.main()
