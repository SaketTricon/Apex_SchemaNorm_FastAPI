import math
from collections import Counter


NULL_VALUES = {
    "",
    "null",
    "none",
    "na",
    "n/a",
    "nan",
}


NUMERIC_TYPES = {
    "integer",
    "numeric",
    "decimal",
    "real",
    "double precision",
}


def is_null(value) -> bool:
    if value is None:
        return True

    return (
        str(value).strip().lower()
        in NULL_VALUES
    )


def to_number(value):
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def percentile(
    values: list[float],
    percentage: float,
):
    if not values:
        return None

    ordered = sorted(values)

    position = (
        percentage / 100
    ) * (len(ordered) - 1)

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    weight = position - lower

    return (
        ordered[lower]
        + (ordered[upper] - ordered[lower])
        * weight
    )


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

        null_count = (
            len(values) - len(non_null)
        )

        distinct_count = len(
            set(non_null)
        )

        lengths = [
            len(value)
            for value in non_null
        ]

        data_type = schema_map.get(
            column,
            "unknown",
        )

        stats = {
            "column": column,
            "data_type": data_type,
            "row_count": len(values),
            "null_count": null_count,
            "null_percentage": round(
                (
                    null_count * 100
                    / len(values)
                ),
                2,
            ) if values else 0,
            "non_null_count": len(non_null),
            "distinct_count": distinct_count,
            "distinct_percentage": round(
                (
                    distinct_count * 100
                    / len(non_null)
                ),
                2,
            ) if non_null else 0,
            "duplicate_value_count": (
                len(non_null)
                - distinct_count
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
            "average_length": round(
                sum(lengths) / len(lengths),
                2,
            ) if lengths else None,
        }

        if data_type in NUMERIC_TYPES:

            numeric_values = [
                number
                for value in non_null
                if (
                    number := to_number(value)
                ) is not None
            ]

            if numeric_values:

                mean = (
                    sum(numeric_values)
                    / len(numeric_values)
                )

                variance = (
                    sum(
                        (value - mean) ** 2
                        for value in numeric_values
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
                        "median": round(
                            percentile(
                                numeric_values,
                                50,
                            ),
                            4,
                        ),
                        "standard_deviation": round(
                            math.sqrt(variance),
                            4,
                        ),
                        "percentile_25": round(
                            percentile(
                                numeric_values,
                                25,
                            ),
                            4,
                        ),
                        "percentile_75": round(
                            percentile(
                                numeric_values,
                                75,
                            ),
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
            for value, count in
            counter.most_common(5)
        ]

        statistics.append(stats)

    return {
        "row_count": len(rows),
        "columns": statistics,
    }
