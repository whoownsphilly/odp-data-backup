import requests
import json
from pathlib import Path
from typing import Any
import pandas as pd
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.main import SQLModelMetaclass
import opa_tables


def make_request(sql):
    response = requests.post("https://phl.carto.com/api/v2/sql", data={"q": sql})
    json = response.json()
    if "rows" not in json:
        raise ValueError(f"{sql}\n\n{json}")
    return json


class OpaService:
    def __init__(self, /, *, db_filepath: str):
        self.db_filepath = db_filepath

        db_str = f"sqlite:///{db_filepath}"
        self.engine = create_engine(db_str)
        SQLModel.metadata.create_all(self.engine)

        # Create a session to interact with the database
        self.session = Session(self.engine)

    def download_split_data(
        self,
        *,
        split_by_field: str,
        distinct_sql: str,
        table: str,
        summary_json: dict[str, Any] | None = None,
        save_to_csv: bool = True,
        save_to_sqlite: bool = True,
        where_str: str | None = None,
    ):
        # Define the path to the folder you want to create
        if save_to_csv:
            Path("csvs").mkdir(parents=True, exist_ok=True)
            Path(f"csvs/{table}").mkdir(parents=True, exist_ok=True)
            if summary_json:
                json.dump(summary_json, open(f"csvs/{table}/summary.json", "w"))

        split_by_sql = f"select distinct({distinct_sql}) as split_field from {table} order by split_field"
        response = make_request(split_by_sql)
        split_values = [x["split_field"] for x in response["rows"]]

        where_sql = f"and {where_str}" if where_str else ""

        for value in split_values:
            print(f"Downloading from {table} for {distinct_sql}: {value}")
            if value is None:
                sql_equivalency_value = " is null"
            else:
                sql_equivalency_value = f" = '{value}'"

            response = make_request(
                f"SELECT * from {table} where {distinct_sql} {sql_equivalency_value} {where_sql}"
            )
            if save_to_csv:
                pd.DataFrame(response["rows"]).to_csv(
                    f"csvs/{table}/{table}_{split_by_field}_{value}.csv", index=False
                )
            if save_to_sqlite:
                self.load_response_to_sqlite(response, table=table)

    def load_response_to_sqlite(self, response: dict[str, Any], /, *, table: str):
        OpaClass = self.get_class_from_table_name(table)
        # self.session.add_all([OpaClass(**row) for row in response["rows"]])
        for row in response["rows"]:
            try:
                self.session.add(OpaClass.validate(row))
                self.session.commit()
            except Exception as exc:
                print(exc)
                breakpoint()

    def get_class_from_table_name(self, table_name: str) -> SQLModel:
        # A janky way to get all the classes defined in opa_tables
        # and returning the one based on the name
        class_obj = {
            cls.__tablename__: cls
            for cls in opa_tables.__dict__.values()
            if isinstance(cls, SQLModelMetaclass) and cls.__tablename__ != "sqlmodel"
        }.get(table_name)
        if not class_obj:
            raise ValueError(f"No SQLModel class made for {table_name} yet...")
        return class_obj
