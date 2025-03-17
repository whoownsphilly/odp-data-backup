import click
from datetime import datetime
import pandas as pd
import json
from pathlib import Path

from services import OpaService
from services import make_request


@click.group
def cli():
    pass


@cli.command
@click.option("--db-filepath", default="open_data_philly.db", show_default=True)
@click.option("--table", required=True)
@click.option("--csv-split-col", required=True)
@click.option("--where-str", default=None)
@click.option("--save-to-csv/--skip-save-to-csv", default=True, show_default=True)
@click.option("--save-to-sqlite/--skip-save-to-sqlite", default=True, show_default=True)
def by_col(
    table: str,
    csv_split_col: str,
    db_filepath: str,
    save_to_csv: bool,
    save_to_sqlite: bool,
    where_str: str | None = None,
):
    """A command to download all data from a table, with separate CSVs per split-by column"""
    response = make_request(f"SELECT * from {table} limit 0")

    columns = [key for key, info in response["fields"].items()]
    if csv_split_col not in columns:
        raise ValueError(f"Column {csv_split_col} not in {table}. Columns: {columns}")

    # Get all the unique values from the split_by.
    # For example, if split_by is zip_code, we are getting all the unique zip_codes
    # for which there is data.
    service = OpaService(db_filepath=db_filepath)
    return service.download_split_data(
        split_by_field=csv_split_col,
        distinct_sql=csv_split_col,
        table=table,
        save_to_csv=save_to_csv,
        save_to_sqlite=save_to_sqlite,
        where_str=where_str,
    )


@cli.command
@click.option("--table", required=True)
@click.option("--db-filepath", default="open_data_philly.db", show_default=True)
@click.option("--save-to-csv/--skip-save-to-csv", default=True, show_default=True)
@click.option("--save-to-sqlite/--skip-save-to-sqlite", default=True, show_default=True)
@click.option(
    "--split-by",
    required=True,
    type=(str, click.Choice(["year"])),
    help="Which column and subsequent granularity to split by, such as 'initialissuedate year'",
)
def by_datetime(
    table: str,
    split_by: tuple[str, str],
    db_filepath: str,
    save_to_csv: bool,
    save_to_sqlite: bool,
):
    """A command to download all data from a table, with separate CSVs per column and time-based split-by option"""
    response = make_request(f"SELECT * from {table} limit 0")
    fields = response["fields"]

    split_by_col, split_by_field = split_by
    tz_columns = [
        key for key, info in response["fields"].items() if info["type"] == "date"
    ]
    if split_by_col not in tz_columns:
        columns = [key for key, _ in fields.items()]
        raise ValueError(f"Column {split_by_col} not in {table}. Columns: {columns}")

    # Get all the unique values from the split_by_field.
    # For example, if split_by_field is year, we are getting all the unique years
    # for which there is data.
    distinct_tz_sql = f"extract({split_by_field} from {split_by_col})"

    first_last_response = make_request(
        f"SELECT min({split_by_col}) as first_dt, max({split_by_col}) as last_dt from {table} limit 1"
    )
    count_by_response = make_request(
        f"SELECT {distinct_tz_sql} as dt, count(*) as num_rows from {table} group by {distinct_tz_sql} order by {distinct_tz_sql} asc"
    )
    summary_json = {
        **first_last_response["rows"][0],
        "value_counts": {r["dt"]: r["num_rows"] for r in count_by_response["rows"]},
    }

    service = OpaService(db_filepath=db_filepath)
    print(f"Data ranges from {summary_json['first_dt']} to {summary_json['last_dt']}")

    return service.download_split_data(
        split_by_field=split_by_field,
        distinct_sql=distinct_tz_sql,
        summary_json=summary_json,
        table=table,
        save_to_csv=save_to_csv,
        save_to_sqlite=save_to_sqlite,
    )


@cli.command
@click.option("--table", required=True)
@click.option("--column", required=True)
def json_file_per_row(table: str, column: str):
    response = make_request(f"SELECT * from {table} limit 0")
    fields = response["fields"]
    available_columns = [key for key, _ in fields.items()]
    if column not in available_columns:
        raise ValueError(
            f"Column {column} not in {table}. Columns: {available_columns}"
        )

    response = make_request(f"SELECT * from {table} limit 10")

    Path("json").mkdir(parents=True, exist_ok=True)
    Path(f"json/{table}").mkdir(parents=True, exist_ok=True)
    for row in response["rows"]:
        with open("json/{table}/{columns}.json") as f:
            json.dump(f, row)


@cli.command
@click.option(
    "--dist-from-hin-threshold",
    default=0.0001,
    show_default=True,
    help="""
--- This shows that 0.0001 is between 8.54427772 and 11.10338786 meters
SELECT ST_Distance(
    ST_GeographyFromText('SRID=4326;POINT(' || -75.14144069 || ' ' || 39.96071159 || ')'),
    ST_GeographyFromText('SRID=4326;POINT(' || (-75.14144069 + 0.0001) || ' ' || 39.96071159 || ')')
) AS distance_in_meters_lng,
ST_Distance(
    ST_GeographyFromText('SRID=4326;POINT(' || -75.14144069 || ' ' || 39.96071159 || ')'),
    ST_GeographyFromText('SRID=4326;POINT(' || (-75.14144069) || ' ' || 39.96071159  + 0.0001 || ')')
) AS distance_in_meters_lat
""",
)
def download_car_ped_stops_relation_to_hin(dist_from_hin_threshold: float):
    source_table = "car_ped_stops"
    table = "car_ped_stops_on_hin"
    split_by_field = "year"
    split_by_col = "datetimeoccur"
    Path("csvs").mkdir(parents=True, exist_ok=True)
    Path(f"csvs/{table}").mkdir(parents=True, exist_ok=True)
    distinct_tz_sql = f"extract({split_by_field} from {split_by_col})"
    first_last_response = make_request(
        f"SELECT min({split_by_col}) as first_dt, max({split_by_col}) as last_dt from {source_table} limit 1"
    )
    count_by_response = make_request(
        f"SELECT {distinct_tz_sql} as dt, count(*) as num_rows from {source_table} group by {distinct_tz_sql} order by {distinct_tz_sql} asc"
    )
    summary_json = {
        **first_last_response["rows"][0],
        "value_counts": {r["dt"]: r["num_rows"] for r in count_by_response["rows"]},
    }
    if summary_json:
        json.dump(summary_json, open(f"csvs/{table}/summary.json", "w"))

    years = list(range(2014, datetime.now().year + 1))
    for value in years:
        print(value)
        response = make_request(
            f"""
        SELECT
            car_ped_stops.*,
            (CASE WHEN hin.street_name is not null
            AND st_y(car_ped_stops.the_geom)<42 and car_ped_stops.the_geom is not null
            THEN 1 ELSE 0 END
            ) as n_stopped_locatable_on_hin,
            (
                case when st_y(car_ped_stops.the_geom)<42 and car_ped_stops.the_geom is not null then 1 else 0 end
            ) as n_stopped_locatable
            FROM car_ped_stops
            LEFT JOIN high_injury_network_2020 hin
            ON ST_DWithin(car_ped_stops.the_geom, hin.the_geom, {dist_from_hin_threshold})
            WHERE extract('year' from datetimeoccur) = '{value}'

        """
        )
        pd.DataFrame(response["rows"]).to_csv(
            f"csvs/{table}/{table}_{split_by_field}_{value}.csv", index=False
        )


if __name__ == "__main__":
    cli()
