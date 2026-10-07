import ipaddress
import re
from collections import Counter
from datetime import datetime


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)

INTEGER_PATTERN = re.compile(
    r"^[+-]?\d+$"
)

NUMERIC_PATTERN = re.compile(
    r"^[+-]?(?:\d+\.\d+|\d+)$"
)

DATE_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}$"
)

DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
)

PHONE_PATTERN = re.compile(
    r"^\+?[0-9][0-9\s().-]{8,}$"
)

URL_PATTERN = re.compile(
    r"^https?://[^\s]+$",
    re.IGNORECASE,
)


NULL_VALUES = {
    "",
    "null",
    "none",
    "na",
    "n/a",
    "nan",
}


def is_null(value) -> bool:
    if value is None:
        return True

    return str(value).strip().lower() in NULL_VALUES


def detect_pattern(value) -> str:

    if is_null(value):
        return "null"

    value = str(value).strip()
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

    try:
        ipaddress.ip_address(value)
        return "ip_address"
    except ValueError:
        pass

    if PHONE_PATTERN.fullmatch(value):
        digits = re.sub(r"\D", "", value)

        if len(digits) >= 10 and (
            any(char in value for char in "+-(). ")
        ):
            return "phone_like"

    if DATE_PATTERN.fullmatch(value):
        try:
            datetime.strptime(
                value,
                "%Y-%m-%d",
            )
            return "date"
        except ValueError:
            pass

    if DATETIME_PATTERN.fullmatch(value):
        try:
            datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
            return "datetime"
        except ValueError:
            return "datetime_like"

    if INTEGER_PATTERN.fullmatch(value):
        return "integer"

    if NUMERIC_PATTERN.fullmatch(value):
        return "numeric"

    return "string"


def profile_column_patterns(
    rows: list[dict],
    column: str,
) -> dict:

    values = [
        row.get(column)
        for row in rows
    ]

    counts = Counter(
        detect_pattern(value)
        for value in values
    )

    non_null_values = [
        str(value).strip()
        for value in values
        if not is_null(value)
    ]

    examples = []

    for value in non_null_values:

        if value not in examples:
            examples.append(value)

        if len(examples) == 5:
            break

    return {
        "patterns": dict(counts),
        "sample_values": examples,
    }
