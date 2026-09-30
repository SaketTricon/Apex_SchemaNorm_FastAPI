import ipaddress
import re
from collections import Counter
from datetime import datetime


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)
INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
DECIMAL_PATTERN = re.compile(r"^[+-]?(?:\d+\.\d+|\d+)$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
)
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s().-]{6,}$")
URL_PATTERN = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)


def detect_pattern(value) -> str:
    if value is None:
        return "null"

    value = str(value).strip()

    if not value:
        return "empty"

    lowered = value.lower()

    if lowered in {"true", "false"}:
        return "boolean"

    if lowered in {"yes", "no", "y", "n"}:
        return "boolean_like"

    if EMAIL_PATTERN.fullmatch(value):
        return "email"

    if UUID_PATTERN.fullmatch(value):
        return "uuid"

    if URL_PATTERN.fullmatch(value):
        return "url"

    if PHONE_PATTERN.fullmatch(value) and any(
        character.isdigit() for character in value
    ):
        return "phone_like"

    if INTEGER_PATTERN.fullmatch(value):
        return "integer"

    if DECIMAL_PATTERN.fullmatch(value):
        return "numeric"

    if DATE_PATTERN.fullmatch(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return "date"
        except ValueError:
            pass

    if DATETIME_PATTERN.fullmatch(value):
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "datetime"
        except ValueError:
            return "datetime_like"

    try:
        ipaddress.ip_address(value)
        return "ip_address"
    except ValueError:
        pass

    return "string"


def profile_sample(
    rows: list[dict],
    columns: list[str],
) -> dict:
    results = []

    for column in columns:
        values = [
            row.get(column)
            for row in rows
            if row.get(column) not in (None, "")
        ]

        string_values = [str(value).strip() for value in values]

        pattern_counts = Counter(
            detect_pattern(value)
            for value in values
        )

        examples = []
        for value in string_values:
            if value not in examples:
                examples.append(value)

            if len(examples) == 5:
                break

        results.append(
            {
                "column": column,
                "sample_non_null_count": len(values),
                "sample_null_count": len(rows) - len(values),
                "sample_distinct_count": len(set(string_values)),
                "example_values": examples,
                "detected_patterns": dict(pattern_counts),
            }
        )

    return {
        "sample_size": len(rows),
        "columns": results,
    }
