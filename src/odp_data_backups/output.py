from __future__ import annotations

import csv
import json
import sqlite3
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .sql import identifier, sqlite_type


def normalize(value: Any) -> Any:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (Mapping, list, tuple)):
        return json.dumps(value, separators=(",", ":"), sort_keys=True)
    return value


class SQLiteOutput:
    """Permissive, metadata-typed SQLite output for a single Carto table."""

    def __init__(self, path: str | Path, table: str, fields: Mapping[str, Mapping[str, Any]]) -> None:
        self.path = Path(path)
        self.table = table
        self.fields = dict(fields)
        self.connection = sqlite3.connect(self.path)

    def reset(self) -> None:
        table = identifier(self.table)
        definitions = ", ".join(
            f"{identifier(name)} {sqlite_type(info.get('type'))}"
            for name, info in self.fields.items()
        )
        with self.connection:
            self.connection.execute(f"DROP TABLE IF EXISTS {table}")
            self.connection.execute(f"CREATE TABLE {table} ({definitions})")

    def write(self, rows: Sequence[Mapping[str, Any]]) -> None:
        if not rows:
            return
        columns = list(self.fields)
        placeholders = ", ".join("?" for _ in columns)
        column_sql = ", ".join(identifier(column) for column in columns)
        statement = (
            f"INSERT INTO {identifier(self.table)} ({column_sql}) "
            f"VALUES ({placeholders})"
        )
        values = ([normalize(row.get(column)) for column in columns] for row in rows)
        with self.connection:
            self.connection.executemany(statement, values)

    def add_indexes(self, columns: Sequence[str]) -> None:
        with self.connection:
            for column in columns:
                if column not in self.fields:
                    raise ValueError(f"Cannot index missing column {column!r}")
                name = f"idx_{self.table}_{column}"
                self.connection.execute(
                    f"CREATE INDEX IF NOT EXISTS {identifier(name)} "
                    f"ON {identifier(self.table)} ({identifier(column)})"
                )

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "SQLiteOutput":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class CSVOutput:
    def __init__(self, path: str | Path, columns: Sequence[str]) -> None:
        self.path = Path(path)
        self.columns = list(columns)
        self.file = None
        self.writer = None

    def write(self, rows: Sequence[Mapping[str, Any]]) -> None:
        if not rows:
            return
        if self.file is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.file = self.path.open("w", newline="", encoding="utf-8")
            self.writer = csv.DictWriter(self.file, fieldnames=self.columns, extrasaction="ignore")
            self.writer.writeheader()
        assert self.writer is not None
        self.writer.writerows(
            {column: normalize(row.get(column)) for column in self.columns}
            for row in rows
        )

    def close(self) -> None:
        if self.file is not None:
            self.file.close()

    def __enter__(self) -> "CSVOutput":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
