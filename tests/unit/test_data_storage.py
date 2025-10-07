import sqlite3
from pathlib import Path

import pytest

from src.lib.data_storage import DataStorage


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "trendline.db"
    schema_path = Path("data/db/schema.sql")
    storage = DataStorage(database_path=db_path, schema_path=schema_path)
    storage.initialize()
    return db_path


def test_data_storage_runs_migrations(temp_db: Path) -> None:
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trendline'")
    row = cursor.fetchone()
    conn.close()
    assert row is not None


def test_data_storage_archival_view(temp_db: Path) -> None:
    storage = DataStorage(database_path=temp_db, schema_path=Path("data/db/schema.sql"))
    with pytest.raises(NotImplementedError):
        storage.create_archive_view("trendline")
