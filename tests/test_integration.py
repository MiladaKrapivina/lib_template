"""Интеграционные тесты персистентности данных."""

import tempfile
import unittest

from src.services.data_manager import DataManager
from src.services.library_service import LibraryService


class PersistenceTests(unittest.TestCase):
    """Проверяет сохранение данных между экземплярами сервиса."""

    def test_data_persists_between_service_instances(self) -> None:
        """Добавленная книга доступна после повторной загрузки сервиса."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = DataManager(temp_dir)
            first = LibraryService(manager)
            first.add_book("b1", "The Hobbit", "J. R. R. Tolkien", 1937, "Fantasy", 4)
            second = LibraryService(DataManager(temp_dir))
            self.assertEqual(second.books["b1"].title, "The Hobbit")


if __name__ == "__main__":
    unittest.main()
