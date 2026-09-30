import re
from collections import Counter
from datetime import datetime


IDENTIFIER_NAME_PATTERN = re.compile(
    r"(^|_)(id|key|code|identifier|uuid|ref|number|no)($|_)",
    re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)
INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
NUMERIC_PATTERN = re.compile(r"^[+-]?(?:\d+\.\d+|\d+)$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
)


def clean_values(values):
    return [
        str(value).strip()
        for value in values
        if value is not None and str(value).strip() != ""
    ]


def is_identifier_like(column_name: str) -> bool:
    return bool(
        IDENTIFIER_NAME_PATTERN.search(column_name)
    )


def infer_csv_type(values: list[str]) -> str:
    values = clean_values(values)

    if not values:
        return "unknown"

    lowered = {value.lower() for value in values}

    if lowered <= {"true", "false"}:
        return "boolean"

    if lowered <= {
        "true",
        "false",
        "yes",
        "no",
        "y",
        "n",
    }:
        return "boolean_like"

    if all(
        INTEGER_PATTERN.fullmatch(value)
        for value in values
    ):
        return "integer"

    if all(
        NUMERIC_PATTERN.fullmatch(value)
        for value in values
    ):
        return "numeric"

    if all(
        DATE_PATTERN.fullmatch(value)
        and is_valid_date(value)
        for value in values
    ):
        return "date"

    if all(
        DATETIME_PATTERN.fullmatch(value)
        for value in values
    ):
        return "datetime"

    if all(
        EMAIL_PATTERN.fullmatch(value)
        for value in values
    ):
        return "email"

    if all(
        UUID_PATTERN.fullmatch(value)
        for value in values
    ):
        return "uuid"

    return "string"


def is_valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def infer_logical_type(
    column_name: str,
    values: list[str],
    data_type: str,
) -> str:
    values = clean_values(values)

    if not values:
        return "unknown"

    lowered_name = column_name.lower()

    if all(
        EMAIL_PATTERN.fullmatch(value)
        for value in values
    ):
        return "email"

    if all(
        UUID_PATTERN.fullmatch(value)
        for value in values
    ):
        return "uuid"

    if is_identifier_like(column_name):
        return "identifier"

    if "date" in lowered_name:
        return "date"

    if (
        "time" in lowered_name
        or lowered_name.endswith("_at")
    ):
        return "datetime"

    if data_type in {"integer", "numeric"}:
        return "numeric"

    if data_type in {
        "boolean",
        "boolean_like",
    }:
        return "boolean"

    return "string"


def profile_csv_schema(
    rows: list[dict],
    columns: list[str],
) -> dict:
    result = []

    for position, column in enumerate(columns, start=1):
        raw_values = [
            row.get(column)
            for row in rows
        ]

        values = clean_values(raw_values)

        data_type = infer_csv_type(values)
        logical_type = infer_logical_type(
            column,
            values,
            data_type,
        )

        distinct_count = len(set(values))

        lengths = [
            len(value)
            for value in values
        ]

        result.append(
            {
                "name": column,
                "ordinal_position": position,
                "data_type": data_type,
                "logical_type": logical_type,
                "nullable": len(values) < len(rows),
                "identifier_like": is_identifier_like(column),
                "sample_unique_like": (
                    len(values) > 0
                    and distinct_count == len(values)
                ),
                "min_length": (
                    min(lengths)
                    if lengths
                    else None
                ),
                "max_length": (
                    max(lengths)
                    if lengths
                    else None
                ),
            }
        )

    return build_schema_summary(result)


def build_schema_summary(columns: list[dict]) -> dict:
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
            if column["data_type"] == "date"
        ],
        "datetime_columns": [
            column["name"]
            for column in columns
            if column["data_type"] == "datetime"
        ],
        "boolean_columns": [
            column["name"]
            for column in columns
            if column["data_type"]
            in {"boolean", "boolean_like"}
        ],
        "numeric_columns": [
            column["name"]
            for column in columns
            if column["data_type"]
            in {"integer", "numeric"}
        ],
        "email_columns": [
            column["name"]
            for column in columns
            if column["logical_type"] == "email"
        ],
        "uuid_columns": [
            column["name"]
            for column in columns
            if column["logical_type"] == "uuid"
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
                c.ordinal_position,
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.column_default
            FROM information_schema.columns c
            WHERE c.table_schema = %s
              AND c.table_name = %s
            ORDER BY c.ordinal_position
            """,
            (schema_name, table_name),
        )

        rows = cursor.fetchall()

        if not rows:
            raise ValueError(
                f"Table '{schema_name}.{table_name}' "
                "was not found."
            )

        cursor.execute(
            """
            SELECT
                kcu.column_name,
                tc.constraint_type,
                ccu.table_name,
                ccu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            LEFT JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
             AND tc.table_schema = ccu.table_schema
            WHERE tc.table_schema = %s
              AND tc.table_name = %s
              AND tc.constraint_type IN (
                  'PRIMARY KEY',
                  'FOREIGN KEY',
                  'UNIQUE'
              )
            """,
            (schema_name, table_name),
        )

        constraints = cursor.fetchall()

    primary_keys = set()
    unique_columns = set()
    foreign_keys = {}

    for (
        column_name,
        constraint_type,
        referenced_table,
        referenced_column,
    ) in constraints:

        if constraint_type == "PRIMARY KEY":
            primary_keys.add(column_name)

        elif constraint_type == "UNIQUE":
            unique_columns.add(column_name)

        elif constraint_type == "FOREIGN KEY":
            foreign_keys[column_name] = {
                "table": referenced_table,
                "column": referenced_column,
            }

    columns = []

    for row in rows:
        (
            ordinal_position,
            name,
            data_type,
            nullable,
            max_length,
            precision,
            scale,
            default_value,
        ) = row

        identifier_like = is_identifier_like(name)

        column = {
            "name": name,
            "ordinal_position": ordinal_position,
            "data_type": data_type,
            "logical_type": infer_postgres_logical_type(
                name,
                data_type,
            ),
            "nullable": nullable == "YES",
            "identifier_like": identifier_like,
            "primary_key": name in primary_keys,
            "unique": name in unique_columns,
            "foreign_key": name in foreign_keys,
            "references": foreign_keys.get(name),
            "max_length": max_length,
            "numeric_precision": precision,
            "numeric_scale": scale,
            "default": default_value,
        }

        columns.append(column)

    return build_schema_summary(columns)


def infer_postgres_logical_type(
    column_name: str,
    data_type: str,
) -> str:

    data_type = data_type.lower()
    column_name = column_name.lower()

    if "timestamp" in data_type:
        return "datetime"

    if data_type == "date":
        return "date"

    if data_type == "boolean":
        return "boolean"

    if data_type in {
        "smallint",
        "integer",
        "bigint",
        "numeric",
        "decimal",
        "real",
        "double precision",
    }:
        return "numeric"

    if (
        "uuid" in data_type
        or column_name.endswith("_uuid")
    ):
        return "uuid"

    if is_identifier_like(column_name):
        return "identifier"

    return "string"
