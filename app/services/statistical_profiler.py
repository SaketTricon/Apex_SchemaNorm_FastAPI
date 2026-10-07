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


def profile_statistics(
    rows: list[dict],
    schema_columns: list[dict],
) -> list[dict]:

    statistics = []

    for schema_column in schema_columns:

        column = schema_column["column_name"]

        values = [
            row.get(column)
            for row in rows
        ]

        non_null = [
            str(value).strip()
            for value in values
            if not is_null(value)
        ]

        row_count = len(values)
        null_count = row_count - len(non_null)
        non_null_count = len(non_null)
        distinct_count = len(set(non_null))
        duplicate_count = non_null_count - distinct_count

        statistics.append(
            {
                "column_name": column,
                "statistics": {
                    "row_count": row_count,
                    "null_count": null_count,
                    "null_percentage": (
                        round(
                            null_count * 100 / row_count,
                            2,
                        )
                        if row_count
                        else 0
                    ),
                    "non_null_count": non_null_count,
                    "distinct_count": distinct_count,
                    "distinct_percentage": (
                        round(
                            distinct_count * 100 / non_null_count,
                            2,
                        )
                        if non_null_count
                        else 0
                    ),
                    "duplicate_value_count": duplicate_count,
                },
            }
        )

    return statistics
