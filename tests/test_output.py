import sqlite3

from odp_data_backups.output import SQLiteOutput


def test_text_column_accepts_integer_schema_drift(tmp_path):
    database = tmp_path / "output.db"
    fields = {
        "address_high": {"type": "string"},
        "details": {"type": "unknown"},
    }

    with SQLiteOutput(database, "rtt_summary", fields) as output:
        output.reset()
        output.write([{"address_high": 24, "details": {"source": "carto"}}])

    connection = sqlite3.connect(database)
    row = connection.execute(
        "SELECT address_high, typeof(address_high), details FROM rtt_summary"
    ).fetchone()
    assert row == ("24", "text", '{"source":"carto"}')


def test_schema_is_derived_from_carto_metadata(tmp_path):
    database = tmp_path / "output.db"
    fields = {
        "name": {"type": "string"},
        "amount": {"type": "number"},
        "active": {"type": "boolean"},
        "created_at": {"type": "date"},
    }

    with SQLiteOutput(database, "example", fields) as output:
        output.reset()

    connection = sqlite3.connect(database)
    schema = connection.execute("PRAGMA table_info(example)").fetchall()
    assert [row[2] for row in schema] == ["TEXT", "NUMERIC", "INTEGER", "TEXT"]
