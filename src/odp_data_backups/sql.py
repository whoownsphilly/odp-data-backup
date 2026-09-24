from __future__ import annotations

import re
from typing import Any


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def identifier(value: str) -> str:
    """Quote a simple PostgreSQL/SQLite identifier after validating it."""
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Invalid table or column name: {value!r}")
    return f'"{value}"'


def literal(value: Any) -> str:
    """Render a value returned by Carto as a safe SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return repr(value)
    return "'" + str(value).replace("'", "''") + "'"


def sqlite_type(carto_type: str | None) -> str:
    """Map Carto metadata to SQLite affinity without validating row values."""
    return {
        "boolean": "INTEGER",
        # NUMERIC preserves integers as integers while still accepting decimals.
        # Carto reports both through the single broad "number" type.
        "number": "NUMERIC",
        "date": "TEXT",
        "string": "TEXT",
        "geometry": "TEXT",
    }.get(carto_type or "", "NUMERIC")
