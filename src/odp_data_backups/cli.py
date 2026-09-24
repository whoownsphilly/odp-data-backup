from __future__ import annotations

import click

from .client import CartoClient
from .downloader import Downloader


def common_options(function):
    options = [
        click.option("--table", required=True, help="Carto table to download."),
        click.option("--db-filepath", default="open_data_philly.db", show_default=True),
        click.option("--where", "where_str", help="Optional Carto SQL filter."),
        click.option("--index", "indexes", multiple=True, help="SQLite column to index."),
        click.option("--page-size", default=25_000, type=click.IntRange(min=1), show_default=True),
        click.option("--endpoint", default="https://phl.carto.com/api/v2/sql", show_default=True),
        click.option("--add-lat-lng/--no-add-lat-lng", default=True, show_default=True),
    ]
    for option in reversed(options):
        function = option(function)
    return function


def make_downloader(endpoint: str, page_size: int) -> Downloader:
    return Downloader(CartoClient(endpoint), page_size=page_size)


@click.group()
def cli() -> None:
    """Download any OpenDataPhilly Carto table to a typed SQLite database."""


@cli.command("table")
@common_options
@click.option("--csv-path", help="Also write a CSV file to this path.")
@click.option("--order-by", help="Stable Carto SQL ordering expression for pagination.")
def download_table(
    table: str,
    db_filepath: str,
    where_str: str | None,
    indexes: tuple[str, ...],
    page_size: int,
    endpoint: str,
    add_lat_lng: bool,
    csv_path: str | None,
    order_by: str | None,
) -> None:
    """Download a complete table, optionally filtered."""
    make_downloader(endpoint, page_size).download(
        table,
        db_filepath=db_filepath,
        csv_path=csv_path,
        where=where_str,
        order_by=order_by,
        indexes=indexes,
        add_lat_lng=add_lat_lng,
    )


@cli.command("by-col")
@common_options
@click.option("--csv-split-col", required=True)
@click.option("--csv-dir", default=None, help="Also write one CSV per split value.")
@click.option("--save-to-csv/--skip-save-to-csv", default=False, hidden=True)
def by_col(
    table: str,
    db_filepath: str,
    where_str: str | None,
    indexes: tuple[str, ...],
    page_size: int,
    endpoint: str,
    add_lat_lng: bool,
    csv_split_col: str,
    csv_dir: str | None,
    save_to_csv: bool,
) -> None:
    """Download a table in chunks defined by a column's values."""
    if save_to_csv and not csv_dir:
        csv_dir = "csvs"
    make_downloader(endpoint, page_size).download_by_column(
        table,
        csv_split_col,
        db_filepath=db_filepath,
        csv_dir=csv_dir,
        where=where_str,
        indexes=indexes,
        add_lat_lng=add_lat_lng,
    )


@cli.command("by-datetime")
@common_options
@click.option(
    "--split-by",
    required=True,
    type=(str, click.Choice(["year", "month", "day"])),
    metavar="COLUMN [year|month|day]",
)
@click.option("--csv-dir", default=None, help="Also write one CSV per time period.")
@click.option("--save-to-csv/--skip-save-to-csv", default=False, hidden=True)
def by_datetime(
    table: str,
    db_filepath: str,
    where_str: str | None,
    indexes: tuple[str, ...],
    page_size: int,
    endpoint: str,
    add_lat_lng: bool,
    split_by: tuple[str, str],
    csv_dir: str | None,
    save_to_csv: bool,
) -> None:
    """Download a table in year, month, or day chunks."""
    if save_to_csv and not csv_dir:
        csv_dir = "csvs"
    column, granularity = split_by
    make_downloader(endpoint, page_size).download_by_datetime(
        table,
        column,
        granularity,
        db_filepath=db_filepath,
        csv_dir=csv_dir,
        where=where_str,
        indexes=indexes,
        add_lat_lng=add_lat_lng,
    )


if __name__ == "__main__":
    cli()
