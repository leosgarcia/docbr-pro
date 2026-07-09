"""SQLite Cache for CNPJ Enrichment."""

import json
import sqlite3
from typing import Any


class CNPJCache:
    """A simple SQLite-based cache for CNPJ enrichment data."""

    def __init__(self, db_path: str = "docbr_cache.sqlite") -> None:
        """
        Initializes the SQLite cache.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cnpj_cache (
                    cnpj TEXT PRIMARY KEY,
                    data TEXT
                )
                """
            )

    def get(self, cnpj: str) -> dict[str, Any] | None:
        """Retrieves CNPJ data from cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM cnpj_cache WHERE cnpj = ?", (cnpj,))
            row = cursor.fetchone()
            if row:
                return dict(json.loads(row[0]))
            return None

    def set(self, cnpj: str, data: dict[str, Any]) -> None:
        """Stores CNPJ data into cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cnpj_cache (cnpj, data) VALUES (?, ?)",
                (cnpj, json.dumps(data)),
            )
