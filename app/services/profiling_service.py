import csv
import random
from pathlib import Path

from app.services.sample_profiler import profile_sample
from app.services.schema_profiler import (
    profile_csv_schema,
    profile_postgres_schema,
)
from app.services.statistical_profiler import (
    profile_statistics,
)


CSV_PATH = Path("data/vendor_dump.csv")

SAMPLE_SIZE = 100


def read_csv():

    with CSV_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(
                "CSV does not contain headers."
            )

        rows = list(reader)

    if not rows:
        raise ValueError(
            "CSV does not contain data."
        )

    return rows


def sample_rows(
    rows: list[dict],
    sample_size: int,
) -> list[dict]:

    if len(rows) <= sample_size:
        return rows

    return random.sample(
        rows,
        sample_size,
    )


def profile_csv() -> dict:

    rows = read_csv()

    columns = list(rows[0].keys())

    sample = sample_rows(
        rows,
        SAMPLE_SIZE,
    )

    schema = profile_csv_schema(
        sample,
        columns,
    )

    sample_profile = profile_sample(
        sample,
        columns,
    )

    statistics = profile_statistics(
        rows,
        columns,
        schema["columns"],
    )

    return {
        "source": {
            "type": "csv",
            "file": CSV_PATH.name,
            "table": "vendor_dump",
        },
        "sample_profiling": sample_profile,
        "schema_profiling": schema,
        "statistical_profiling": statistics,
    }


def profile_postgres(
    connection,
    schema_name: str,
    table_name: str,
) -> dict:

    schema = profile_postgres_schema(
        connection,
        schema_name,
        table_name,
    )

    columns = [
        column["name"]
        for column in schema["columns"]
    ]

    with connection.cursor() as cursor:

        cursor.execute(
            f'''
            SELECT *
            FROM "{schema_name}"."{table_name}"
            '''
        )

        database_rows = cursor.fetchall()

        column_names = [
            description.name
            for description in cursor.description
        ]

    rows = [
        dict(
            zip(
                column_names,
                row,
            )
        )
        for row in database_rows
    ]

    if not rows:
        raise ValueError(
            f"Table '{schema_name}.{table_name}' is empty."
        )

    sample = sample_rows(
        rows,
        SAMPLE_SIZE,
    )

    sample_profile = profile_sample(
        sample,
        columns,
    )

    statistics = profile_statistics(
        rows,
        columns,
        schema["columns"],
    )

    return {
        "source": {
            "type": "postgresql",
            "schema": schema_name,
            "table": table_name,
        },
        "sample_profiling": sample_profile,
        "schema_profiling": schema,
        "statistical_profiling": statistics,
    }
