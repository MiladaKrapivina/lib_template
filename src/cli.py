"""Консольный интерфейс системы управления библиотекой."""

from src.services.library_service import LibraryError, LibraryService


class LibraryCLI:
    """Простое меню для ролей библиотекаря и читателя."""

    def __init__(self, service: LibraryService | None = None) -> None:
        """Создаёт CLI и подключает сервисный слой."""
        self.service = service or LibraryService()

    def run(self) -> None:
        """Запускает основной цикл выбора роли пользователя."""
        while True:
            print("\n1. Библиотекарь\n2. Читатель\n0. Выход")
            choice = input("Выберите роль: ").strip()
            if choice == "1":
                self._librarian_menu()
            elif choice == "2":
                self._reader_menu()
            elif choice == "0":
                print("До свидания!")
                return
            else:
                print("Некорректный пункт меню")

    def _librarian_menu(self) -> None:
        """Обрабатывает базовые операции библиотекаря."""
        actions = {
            "1": self._add_book,
            "2": self._register_reader,
            "3": self._issue_book,
            "4": self._return_book,
            "5": self._print_books,
        }
        print("\n1. Добавить книгу\n2. Зарегистрировать читателя\n3. Выдать книгу\n4. Вернуть книгу\n5. Список книг")
        action = actions.get(input("Выберите действие: ").strip())
        if action:
            self._safe_call(action)
        else:
            print("Некорректный пункт меню")

    def _reader_menu(self) -> None:
        """Обрабатывает доступные читателю операции поиска книг."""
        self._safe_call(self._print_books)

    def _safe_call(self, action) -> None:
        """Выполняет действие и выводит понятную ошибку вместо аварийного завершения."""
        try:
            action()
        except (LibraryError, ValueError) as exc:
            print(f"Ошибка: {exc}")

    def _add_book(self) -> None:
        """Запрашивает данные книги и добавляет её в фонд."""
        self.service.add_book(input("ID/ISBN: "), input("Название: "), input("Автор: "), int(input("Год: ")), input("Жанр: "), int(input("Экземпляры: ")))
        print("Книга добавлена")

    def _register_reader(self) -> None:
        """Запрашивает данные и регистрирует читателя."""
        self.service.register_reader(input("Номер билета: "), input("ФИО: "), input("Телефон: "))
        print("Читатель зарегистрирован")

    def _issue_book(self) -> None:
        """Оформляет выдачу книги по идентификаторам."""
        tx = self.service.issue_book(input("ID книги: "), input("Номер билета: "))
        print(f"Выдача оформлена: {tx.transaction_id}, вернуть до {tx.due_date}")

    def _return_book(self) -> None:
        """Фиксирует возврат книги по номеру операции."""
        tx = self.service.return_book(input("ID выдачи: "))
        print(f"Возврат оформлен. Штраф: {tx.fine:.2f}")

    def _print_books(self) -> None:
        """Выводит найденные книги и число свободных экземпляров."""
        query = input("Поиск по названию/автору (Enter — все): ")
        for book in self.service.search_books(query):
            print(f"{book.book_id}: {book.title} — {book.author}, {book.year}, {book.genre}; доступно {self.service.available_copies(book.book_id)}")
