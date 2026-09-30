import re


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


def detect_pattern(value: str) -> str:
    value = value.strip()

    if not value:
        return "empty"

    if value.lower() in {"true", "false"}:
        return "boolean"

    if EMAIL_PATTERN.match(value):
        return "email"

    if UUID_PATTERN.match(value):
        return "uuid"

    if re.fullmatch(r"[+-]?\d+", value):
        return "integer"

    if re.fullmatch(r"[+-]?\d*\.\d+", value):
        return "decimal"

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return "date"

    if re.fullmatch(
        r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}.*",
        value,
    ):
        return "datetime"

    return "string"


def profile_sample(
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

        patterns = {}

        for value in values:
            pattern = detect_pattern(str(value))
            patterns[pattern] = patterns.get(pattern, 0) + 1

        examples = []

        for value in values:
            value = str(value)

            if value not in examples:
                examples.append(value)

            if len(examples) == 5:
                break

        result.append(
            {
                "column": column,
                "sample_non_null_count": len(values),
                "sample_null_count": len(rows) - len(values),
                "sample_distinct_count": len(set(map(str, values))),
                "example_values": examples,
                "detected_patterns": patterns,
            }
        )

    return {
        "sample_size": len(rows),
        "columns": result,
    }
