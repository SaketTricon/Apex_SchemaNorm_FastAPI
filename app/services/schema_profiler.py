import re
from collections import Counter


IDENTIFIER_PATTERN = re.compile(
    r"(^|_)(id|key|code|identifier|uuid|ref)($|_)"
)


def infer_csv_type(values: list[str]) -> str:

    values = [
        str(value).strip()
        for value in values
        if value not in (None, "")
    ]

    if not values:
        return "unknown"

    lowered = {value.lower() for value in values}

    if lowered <= {"true", "false"}:
        return "boolean"

    if all(re.fullmatch(r"[+-]?\d+", value) for value in values):
        return "integer"

    if all(
        re.fullmatch(
            r"[+-]?(\d+\.\d+|\d+)",
            value,
        )
        for value in values
    ):
        return "numeric"

    if all(
        re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)
        for value in values
    ):
        return "date"

    if all(
        re.fullmatch(
            r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}.*",
            value,
        )
        for value in values
    ):
        return "datetime"

    return "string"


def is_identifier_like(column_name: str) -> bool:

    return bool(
        IDENTIFIER_PATTERN.search(
            column_name.lower()
        )
    )


def profile_csv_schema(
    rows: list[dict],
    columns: list[str],
) -> dict:

    result = []

    for column in columns:

        values = [
            row.get(column)
            for row in rows
            if row.get(column) not in (None, "")
        ]

        data_type = infer_csv_type(
            values
        )

        result.append(
            {
                "name": column,
                "data_type": data_type,
                "nullable": len(values) < len(rows),
                "identifier_like": is_identifier_like(
                    column
                ),
            }
        )

    return {
        "column_count": len(result),
        "columns": result,
        "identifier_candidates": [
            column["name"]
            for column in result
            if column["identifier_like"]
        ],
        "date_columns": [
            column["name"]
            for column in result
            if column["data_type"] in {
                "date",
                "datetime",
            }
        ],
        "boolean_columns": [
            column["name"]
            for column in result
            if column["data_type"] == "boolean"
        ],
        "numeric_columns": [
            column["name"]
            for column in result
            if column["data_type"] in {
                "integer",
                "numeric",
            }
        ],
    }


def profile_postgres_schema(
    connection,
    schema_name: str,
    table_name: str,
) -> dict:

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position
            """,
            (schema_name, table_name),
        )

        rows = cursor.fetchall()

    if not rows:
        raise ValueError(
            f"Table '{schema_name}.{table_name}' was not found."
        )

    columns = []

    for name, data_type, nullable in rows:

        identifier_like = is_identifier_like(name)

        columns.append(
            {
                "name": name,
                "data_type": data_type,
                "nullable": nullable == "YES",
                "identifier_like": identifier_like,
            }
        )

    return {
        "column_count": len(columns),
        "columns": columns,
        "identifier_candidates": [
            column["name"]
            for column in columns
            if column["identifier_like"]
        ],
        "date_columns": [
            column["name"]
            for column in columns
            if "date" in column["data_type"]
            or "timestamp" in column["data_type"]
        ],
        "boolean_columns": [
            column["name"]
            for column in columns
            if column["data_type"] == "boolean"
        ],
        "numeric_columns": [
            column["name"]
            for column in columns
            if column["data_type"] in {
                "smallint",
                "integer",
                "bigint",
                "numeric",
                "decimal",
                "real",
                "double precision",
            }
        ],
    }
