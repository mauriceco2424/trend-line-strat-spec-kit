"""Utility helpers for loading JSON schemas used in contract tests."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict

SCHEMA_ROOT = (
    Path(__file__).resolve().parents[2]
    / "specs"
    / "001-trendline-breakout"
    / "contracts"
)


class SchemaNotFoundError(FileNotFoundError):
    """Raised when a schema file cannot be located."""


@lru_cache(maxsize=16)
def load_schema(name: str) -> Dict:
    """Load a schema by logical name.

    Parameters
    ----------
    name: str
        Logical schema identifier (filename without extension).
    """

    if not name:
        raise ValueError("Schema name must be provided")

    schema_path = SCHEMA_ROOT / f"{name}.json"
    if not schema_path.exists():
        raise SchemaNotFoundError(f"Schema '{name}' not found at {schema_path}")

    import json

    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
