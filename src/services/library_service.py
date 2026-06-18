"""Сервисный слой с бизнес-логикой управления библиотечным фондом."""

from datetime import date, datetime, timedelta
from uuid import uuid4

from src.models.book import Book
from src.models.reader import Reader
from src.models.transaction import Transaction
from src.services.data_manager import DataManager
from src.utils.validators import require_text, validate_phone, validate_positive_int, validate_year


class LibraryError(Exception):
    """Базовое исключение бизнес-логики библиотеки."""


class LibraryService:
    """Фасад для CRUD книг, управления читателями, выдач и возвратов."""

    def __init__(self, data_manager: DataManager | None = None, fine_per_day: float = 10.0) -> None:
        """Загружает данные и задаёт размер ежедневного штрафа за просрочку."""
        self.data_manager = data_manager or DataManager()
        self.fine_per_day = fine_per_day
        self.books = {row["book_id"]: Book.from_dict(row) for row in self.data_manager.load("books")}
        self.readers = {row["reader_id"]: Reader.from_dict(row) for row in self.data_manager.load("readers")}
        self.transactions = {
            row["transaction_id"]: Transaction.from_dict(row)
            for row in self.data_manager.load("transactions")
        }

    def save_all(self) -> None:
        """Сохраняет все коллекции в JSON-хранилище."""
        self.data_manager.save("books", [book.to_dict() for book in self.books.values()])
        self.data_manager.save("readers", [reader.to_dict() for reader in self.readers.values()])
        self.data_manager.save("transactions", [tx.to_dict() for tx in self.transactions.values()])

    def add_book(self, book_id: str, title: str, author: str, year: int, genre: str, copies: int) -> Book:
        """Добавляет книгу с уникальным идентификатором в фонд."""
        book_id = require_text(book_id, "ID книги")
        if book_id in self.books:
            raise LibraryError("Книга с таким ID уже существует")
        book = Book(book_id, require_text(title, "название"), require_text(author, "автор"), validate_year(year), require_text(genre, "жанр"), validate_positive_int(copies, "экземпляры"))
        self.books[book_id] = book
        self.save_all()
        return book

    def update_book(self, book_id: str, **changes: object) -> Book:
        """Редактирует поля существующей книги."""
        book = self._get_book(book_id)
        for field in ("title", "author", "genre"):
            if field in changes and changes[field] is not None:
                setattr(book, field, require_text(str(changes[field]), field))
        if changes.get("year") is not None:
            book.year = validate_year(int(changes["year"]))
        if changes.get("copies") is not None:
            copies = validate_positive_int(int(changes["copies"]), "экземпляры")
            if copies < self._active_issues_count(book_id):
                raise LibraryError("Количество экземпляров не может быть меньше активных выдач")
            book.copies = copies
        self.save_all()
        return book

    def delete_book(self, book_id: str) -> None:
        """Удаляет книгу, если она не находится в активных выдачах."""
        self._get_book(book_id)
        if self._active_issues_count(book_id):
            raise LibraryError("Нельзя удалить книгу с активными выдачами")
        del self.books[book_id]
        self.save_all()

    def search_books(self, query: str = "", genre: str | None = None) -> list[Book]:
        """Возвращает книги с поиском по названию/автору и фильтром по жанру."""
        query = query.lower().strip()
        genre_filter = genre.lower().strip() if genre else None
        return [
            book for book in self.books.values()
            if (not query or query in book.title.lower() or query in book.author.lower())
            and (not genre_filter or book.genre.lower() == genre_filter)
        ]

    def register_reader(self, reader_id: str, full_name: str, phone: str, registration_date: str | None = None) -> Reader:
        """Регистрирует нового читателя с уникальным номером билета."""
        reader_id = require_text(reader_id, "номер читательского билета")
        if reader_id in self.readers:
            raise LibraryError("Читатель с таким номером уже существует")
        reader = Reader(reader_id, require_text(full_name, "ФИО"), validate_phone(phone), registration_date or date.today().isoformat())
        self.readers[reader_id] = reader
        self.save_all()
        return reader

    def update_reader(self, reader_id: str, **changes: str) -> Reader:
        """Обновляет ФИО или телефон зарегистрированного читателя."""
        reader = self._get_reader(reader_id)
        if changes.get("full_name") is not None:
            reader.full_name = require_text(changes["full_name"], "ФИО")
        if changes.get("phone") is not None:
            reader.phone = validate_phone(changes["phone"])
        self.save_all()
        return reader

    def issue_book(self, book_id: str, reader_id: str, days: int = 14) -> Transaction:
        """Оформляет выдачу книги, если есть доступные экземпляры и нет просрочек."""
        self._get_book(book_id)
        self._get_reader(reader_id)
        if self.available_copies(book_id) < 1:
            raise LibraryError("Нет свободных экземпляров книги")
        if self.reader_overdue_transactions(reader_id):
            raise LibraryError("У читателя есть просроченные книги")
        issue_date = date.today()
        tx = Transaction(str(uuid4()), book_id, reader_id, issue_date.isoformat(), (issue_date + timedelta(days=validate_positive_int(days, "срок выдачи"))).isoformat())
        self.transactions[tx.transaction_id] = tx
        self.save_all()
        return tx

    def return_book(self, transaction_id: str, return_date: str | None = None) -> Transaction:
        """Фиксирует возврат книги и начисляет штраф при просрочке."""
        tx = self._get_transaction(transaction_id)
        if not tx.is_active:
            raise LibraryError("Эта выдача уже закрыта")
        returned = self._parse_date(return_date) if return_date else date.today()
        due = self._parse_date(tx.due_date)
        tx.return_date = returned.isoformat()
        tx.fine = max((returned - due).days, 0) * self.fine_per_day
        self.save_all()
        return tx

    def available_copies(self, book_id: str) -> int:
        """Возвращает количество свободных экземпляров книги."""
        book = self._get_book(book_id)
        return book.copies - self._active_issues_count(book_id)

    def history_for_book(self, book_id: str) -> list[Transaction]:
        """Возвращает историю выдач конкретной книги."""
        self._get_book(book_id)
        return [tx for tx in self.transactions.values() if tx.book_id == book_id]

    def history_for_reader(self, reader_id: str) -> list[Transaction]:
        """Возвращает историю выдач конкретного читателя."""
        self._get_reader(reader_id)
        return [tx for tx in self.transactions.values() if tx.reader_id == reader_id]

    def reader_overdue_transactions(self, reader_id: str) -> list[Transaction]:
        """Возвращает активные просроченные выдачи читателя."""
        today = date.today()
        return [tx for tx in self.history_for_reader(reader_id) if tx.is_active and self._parse_date(tx.due_date) < today]

    def _active_issues_count(self, book_id: str) -> int:
        """Подсчитывает активные выдачи книги."""
        return sum(1 for tx in self.transactions.values() if tx.book_id == book_id and tx.is_active)

    def _get_book(self, book_id: str) -> Book:
        """Возвращает книгу или выбрасывает бизнес-ошибку."""
        try:
            return self.books[book_id]
        except KeyError as exc:
            raise LibraryError("Книга не найдена") from exc

    def _get_reader(self, reader_id: str) -> Reader:
        """Возвращает читателя или выбрасывает бизнес-ошибку."""
        try:
            return self.readers[reader_id]
        except KeyError as exc:
            raise LibraryError("Читатель не найден") from exc

    def _get_transaction(self, transaction_id: str) -> Transaction:
        """Возвращает выдачу или выбрасывает бизнес-ошибку."""
        try:
            return self.transactions[transaction_id]
        except KeyError as exc:
            raise LibraryError("Операция выдачи не найдена") from exc

    @staticmethod
    def _parse_date(value: str) -> date:
        """Разбирает дату ISO-формата YYYY-MM-DD."""
        return datetime.strptime(value, "%Y-%m-%d").date()
