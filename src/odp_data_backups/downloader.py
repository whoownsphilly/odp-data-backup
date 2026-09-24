from __future__ import annotations

import json
import re
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from .client import CartoClient
from .output import CSVOutput, SQLiteOutput
from .sql import identifier, literal


class Downloader:
    def __init__(self, client: CartoClient, *, page_size: int = 25_000) -> None:
        self.client = client
        self.page_size = page_size

    def fields(self, table: str, *, add_lat_lng: bool = True) -> dict[str, dict[str, Any]]:
        table_sql = identifier(table)
        fields = dict(self.client.query(f"SELECT * FROM {table_sql} LIMIT 0")["fields"])
        if add_lat_lng and "the_geom" in fields:
            fields["lng"] = {"type": "number"}
            fields["lat"] = {"type": "number"}
        return fields

    def download(
        self,
        table: str,
        *,
        db_filepath: str = "open_data_philly.db",
        csv_path: str | None = None,
        where: str | None = None,
        order_by: str | None = None,
        indexes: tuple[str, ...] = (),
        add_lat_lng: bool = True,
    ) -> int:
        fields = self.fields(table, add_lat_lng=add_lat_lng)
        query = self._select_query(table, fields, where=where, order_by=order_by)
        return self._write_query(
            table,
            fields,
            query,
            db_filepath=db_filepath,
            csv_path=csv_path,
            indexes=indexes,
        )

    def download_by_column(
        self,
        table: str,
        column: str,
        *,
        db_filepath: str = "open_data_philly.db",
        csv_dir: str | None = None,
        where: str | None = None,
        indexes: tuple[str, ...] = (),
        add_lat_lng: bool = True,
    ) -> int:
        fields = self.fields(table, add_lat_lng=add_lat_lng)
        if column not in fields:
            raise ValueError(f"Column {column!r} not found in {table!r}")
        split_expression = identifier(column)
        return self._download_splits(
            table,
            fields,
            split_expression,
            column,
            db_filepath=db_filepath,
            csv_dir=csv_dir,
            where=where,
            indexes=indexes,
        )

    def download_by_datetime(
        self,
        table: str,
        column: str,
        granularity: str,
        *,
        db_filepath: str = "open_data_philly.db",
        csv_dir: str | None = None,
        where: str | None = None,
        indexes: tuple[str, ...] = (),
        add_lat_lng: bool = True,
    ) -> int:
        if granularity not in {"year", "month", "day"}:
            raise ValueError("granularity must be year, month, or day")
        fields = self.fields(table, add_lat_lng=add_lat_lng)
        if column not in fields:
            raise ValueError(f"Column {column!r} not found in {table!r}")
        split_expression = f"extract({granularity} from {identifier(column)})"
        return self._download_splits(
            table,
            fields,
            split_expression,
            granularity,
            db_filepath=db_filepath,
            csv_dir=csv_dir,
            where=where,
            indexes=indexes,
        )

    def _download_splits(
        self,
        table: str,
        fields: dict[str, dict[str, Any]],
        expression: str,
        split_name: str,
        *,
        db_filepath: str,
        csv_dir: str | None,
        where: str | None,
        indexes: tuple[str, ...],
    ) -> int:
        table_sql = identifier(table)
        filter_sql = f" WHERE {where}" if where else ""
        split_query = (
            f"SELECT DISTINCT {expression} AS split_value FROM {table_sql}"
            f"{filter_sql} ORDER BY split_value"
        )
        split_values = [row["split_value"] for row in self.client.query(split_query)["rows"]]

        total = 0
        with SQLiteOutput(db_filepath, table, fields) as sqlite_output:
            sqlite_output.reset()
            for value in split_values:
                condition = (
                    f"{expression} IS NULL" if value is None else f"{expression} = {literal(value)}"
                )
                combined_where = f"({condition})"
                if where:
                    combined_where += f" AND ({where})"
                query = self._select_query(table, fields, where=combined_where)
                csv_path = None
                if csv_dir:
                    safe_value = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value))
                    csv_path = str(Path(csv_dir) / table / f"{table}_{split_name}_{safe_value}.csv")
                count = self._append_query(sqlite_output, fields, query, csv_path)
                total += count
                print(f"Downloaded {table} {split_name}={value} ({count} rows)")
            sqlite_output.add_indexes(indexes)
        return total

    def _write_query(
        self,
        table: str,
        fields: dict[str, dict[str, Any]],
        query: str,
        *,
        db_filepath: str,
        csv_path: str | None,
        indexes: tuple[str, ...],
    ) -> int:
        with SQLiteOutput(db_filepath, table, fields) as sqlite_output:
            sqlite_output.reset()
            count = self._append_query(sqlite_output, fields, query, csv_path)
            sqlite_output.add_indexes(indexes)
        print(f"Downloaded {table} ({count} rows)")
        return count

    def _append_query(
        self,
        sqlite_output: SQLiteOutput,
        fields: dict[str, dict[str, Any]],
        query: str,
        csv_path: str | None,
    ) -> int:
        count = 0
        with ExitStack() as stack:
            csv_output = (
                stack.enter_context(CSVOutput(csv_path, list(fields))) if csv_path else None
            )
            for rows in self.client.iter_query(query, page_size=self.page_size):
                sqlite_output.write(rows)
                if csv_output:
                    csv_output.write(rows)
                count += len(rows)
        return count

    @staticmethod
    def _select_query(
        table: str,
        fields: dict[str, dict[str, Any]],
        *,
        where: str | None = None,
        order_by: str | None = None,
    ) -> str:
        select = "*"
        if "lng" in fields and "lat" in fields:
            select += ", st_x(the_geom) AS lng, st_y(the_geom) AS lat"
        query = f"SELECT {select} FROM {identifier(table)}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        elif "cartodb_id" in fields:
            query += f" ORDER BY {identifier('cartodb_id')}"
        return query
