"""Слой персистентности для хранения данных библиотеки в JSON-файлах."""

import json
from pathlib import Path
from typing import Any


class DataManager:
    """Читает и записывает коллекции сущностей в отдельные JSON-файлы."""

    def __init__(self, data_dir: str | Path = "data") -> None:
        """Создаёт менеджер данных и каталог хранения при необходимости."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self, name: str) -> list[dict[str, Any]]:
        """Загружает список словарей из файла; при отсутствии файла возвращает список."""
        path = self.data_dir / f"{name}.json"
        if not path.exists():
            return []
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Файл {path} повреждён") from exc
        if not isinstance(data, list):
            raise ValueError(f"Файл {path} должен содержать список")
        return data

    def save(self, name: str, rows: list[dict[str, Any]]) -> None:
        """Сохраняет список словарей в JSON-файл с читаемым форматированием."""
        path = self.data_dir / f"{name}.json"
        with path.open("w", encoding="utf-8") as file:
            json.dump(rows, file, ensure_ascii=False, indent=2)
