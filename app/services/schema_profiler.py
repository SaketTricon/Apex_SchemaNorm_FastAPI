import ipaddress
import re
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

NUMERIC_PATTERN = re.compile(
    r"^[+-]?(?:\d+\.\d+|\d+)$"
)

DATE_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}$"
)

DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
)

NULL_VALUES = {
    "",
    "null",
    "none",
    "na",
    "n/a",
    "nan",
}


def clean_values(values):
    return [
        str(value).strip()
        for value in values
        if not is_null(value)
    ]


def is_null(value):
    if value is None:
        return True

    return str(value).strip().lower() in NULL_VALUES


def is_identifier_like(column_name: str) -> bool:
    return bool(
        IDENTIFIER_NAME_PATTERN.search(column_name)
    )


def is_valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
        return True
    except ValueError:
        return False


def is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def infer_csv_type(values: list[str]) -> str:
    values = clean_values(values)

    if not values:
        return "unknown"

    lowered = {
        value.lower()
        for value in values
    }

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
        EMAIL_PATTERN.fullmatch(value)
        for value in values
    ):
        return "string"

    if all(
        UUID_PATTERN.fullmatch(value)
        for value in values
    ):
        return "string"

    if all(
        DATE_PATTERN.fullmatch(value)
        and is_valid_date(value)
        for value in values
    ):
        return "date"

    if all(
        DATETIME_PATTERN.fullmatch(value)
        and is_valid_datetime(value)
        for value in values
    ):
        return "datetime"

    if all(
        is_ip_address(value)
        for value in values
    ):
        return "string"

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

    return "string"


def infer_semantic_type(
    column_name: str,
    values: list[str],
    data_type: str,
) -> str:

    values = clean_values(values)

    if not values:
        return "unknown"

    name = column_name.lower()

    if all(
        EMAIL_PATTERN.fullmatch(value)
        for value in values
    ):
        return "email"

    if all(
        UUID_PATTERN.fullmatch(value)
        for value in values
    ):
        return "identifier"

    if all(
        is_ip_address(value)
        for value in values
    ):
        return "ip_address"

    if "email" in name:
        return "email"

    if (
        "phone" in name
        or "mobile" in name
        or "telephone" in name
    ):
        return "phone_number"

    if name in {"city", "town"}:
        return "city"

    if (
        "street" in name
        or "address" in name
        or "zip" in name
        or "postal" in name
        or "country" in name
        or "state" in name
    ):
        return "address"

    # Timestamp fields
    if (
        "created" in name
        or "updated" in name
        or "modified" in name
        or "last_login" in name
        or name.endswith("_at")
    ):
        return "timestamp"

    if "date" in name:
        return "date"

    if (
        "price" in name
        or "amount" in name
        or "cost" in name
        or "salary" in name
        or "revenue" in name
    ):
        return "monetary_amount"

    if (
        "quantity" in name
        or "count" in name
        or "age" in name
    ):
        return "numeric_measure"

    if is_identifier_like(column_name):
        return "identifier"

    if data_type in {
        "integer",
        "numeric",
    }:
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

    for position, column in enumerate(
        columns,
        start=1,
    ):
        raw_values = [
            row.get(column)
            for row in rows
        ]

        values = clean_values(raw_values)

        data_type = infer_csv_type(values)

        semantic_type = infer_semantic_type(
            column,
            values,
            data_type,
        )

        result.append(
            {
                "column_name": column,
                "position": position,
                "inferred_data_type": data_type,
                "semantic_type": semantic_type,
                "nullable": len(values) < len(rows),
            }
        )

    return {
        "column_count": len(columns),
        "columns": result,
    }
