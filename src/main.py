"""Точка входа в приложение управления библиотечным фондом."""

from src.cli import LibraryCLI


def main() -> None:
    """Запускает консольный интерфейс приложения."""
    LibraryCLI().run()


if __name__ == "__main__":
    main()
