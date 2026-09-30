import math
from collections import Counter


NULL_VALUES = {
    "",
    "null",
    "none",
    "na",
    "n/a",
}


def is_null(value) -> bool:

    if value is None:
        return True

    return str(value).strip().lower() in NULL_VALUES


def to_number(value):

    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def profile_statistics(
    rows: list[dict],
    columns: list[str],
    schema_columns: list[dict],
) -> dict:

    schema_map = {
        column["name"]: column["data_type"]
        for column in schema_columns
    }

    statistics = []

    for column in columns:

        values = [
            row.get(column)
            for row in rows
        ]

        non_null = [
            str(value).strip()
            for value in values
            if not is_null(value)
        ]

        null_count = len(values) - len(non_null)

        distinct_count = len(set(non_null))

        lengths = [
            len(value)
            for value in non_null
        ]

        stats = {
            "column": column,
            "data_type": schema_map.get(
                column,
                "unknown",
            ),
            "row_count": len(values),
            "null_count": null_count,
            "null_percentage": round(
                null_count * 100 / len(values),
                2,
            ) if values else 0,
            "non_null_count": len(non_null),
            "distinct_count": distinct_count,
            "distinct_percentage": round(
                distinct_count * 100 / len(non_null),
                2,
            ) if non_null else 0,
            "duplicate_value_count": (
                len(non_null) - distinct_count
            ),
            "min_length": min(lengths)
            if lengths else None,
            "max_length": max(lengths)
            if lengths else None,
            "average_length": round(
                sum(lengths) / len(lengths),
                2,
            ) if lengths else None,
        }

        data_type = schema_map.get(
            column,
            "string",
        )

        if data_type in {
            "integer",
            "numeric",
            "decimal",
            "real",
            "double precision",
        }:

            numeric_values = [
                number
                for value in non_null
                if (number := to_number(value))
                is not None
            ]

            if numeric_values:

                mean = (
                    sum(numeric_values)
                    / len(numeric_values)
                )

                variance = (
                    sum(
                        (x - mean) ** 2
                        for x in numeric_values
                    )
                    / len(numeric_values)
                )

                stats.update(
                    {
                        "minimum": min(
                            numeric_values
                        ),
                        "maximum": max(
                            numeric_values
                        ),
                        "average": round(
                            mean,
                            4,
                        ),
                        "standard_deviation": round(
                            math.sqrt(variance),
                            4,
                        ),
                    }
                )

        counter = Counter(non_null)

        stats["top_values"] = [
            {
                "value": value,
                "count": count,
            }
            for value, count in counter.most_common(5)
        ]

        statistics.append(stats)

    return {
        "row_count": len(rows),
        "columns": statistics,
    }
