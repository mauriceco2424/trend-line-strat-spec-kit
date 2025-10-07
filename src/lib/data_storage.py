from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


class DataStorage:
    """Lightweight SQLite helper for backtesting persistence."""

    def __init__(self, database_path: Path | str, schema_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.schema_path = Path(schema_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        try:
            with self.schema_path.open("r", encoding="utf-8") as handle:
                script = handle.read()
            connection.executescript(script)
            connection.commit()
        finally:
            connection.close()

    def create_archive_view(self, table_name: str) -> None:
        raise NotImplementedError("Archive view creation is implemented in later phase")

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)
