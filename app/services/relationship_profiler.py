NULL_VALUES = {
    "",
    "null",
    "none",
    "na",
    "n/a",
    "nan",
}


def get_column_values(
    rows: list[dict],
    column: str,
) -> list[str]:

    return [
        str(row[column]).strip()
        for row in rows
        if row.get(column) is not None
        and str(row[column]).strip().lower()
        not in NULL_VALUES
    ]


def find_candidate_primary_keys(
    rows: list[dict],
    schema_columns: list[dict],
) -> list[dict]:

    total_rows = len(rows)

    candidates = []

    if total_rows == 0:
        return candidates

    for column in schema_columns:

        name = column["column_name"]
        semantic_type = column["semantic_type"]

        # Only identifier-like columns can be
        # considered candidate primary keys.
        if semantic_type != "identifier":
            continue

        values = get_column_values(
            rows,
            name,
        )

        if len(values) != total_rows:
            continue

        distinct_count = len(
            set(values)
        )

        if distinct_count != total_rows:
            continue

        candidates.append(
            {
                "column": name,
                "candidate_primary_key": True,
                "uniqueness_percentage": 100.0,
            }
        )

    return candidates


def find_foreign_keys(
    files: list[dict],
) -> list[dict]:

    relationships = []

    for source_file in files:

        source_name = source_file["file_name"]
        source_rows = source_file["rows"]
        source_schema = source_file["schema"]

        source_pk_names = {
            candidate["column"]
            for candidate in source_file[
                "candidate_primary_keys"
            ]
        }

        for target_file in files:

            target_name = target_file["file_name"]

            if source_name == target_name:
                continue

            target_rows = target_file["rows"]
            target_schema = target_file["schema"]

            target_pk_candidates = target_file[
                "candidate_primary_keys"
            ]

            if not target_pk_candidates:
                continue

            target_schema_map = {
                column["column_name"]: column
                for column in target_schema["columns"]
            }

            for source_column in source_schema["columns"]:

                source_column_name = source_column[
                    "column_name"
                ]

                if source_column_name in source_pk_names:
                    continue

                source_values = set(
                    get_column_values(
                        source_rows,
                        source_column_name,
                    )
                )

                if not source_values:
                    continue

                for target_pk in target_pk_candidates:

                    target_column_name = target_pk[
                        "column"
                    ]

                    target_values = set(
                        get_column_values(
                            target_rows,
                            target_column_name,
                        )
                    )

                    if not target_values:
                        continue

                    # A foreign key must reference
                    # values that actually exist in
                    # the target key.
                    if not source_values.issubset(
                        target_values
                    ):
                        continue

                    target_column = target_schema_map[
                        target_column_name
                    ]

                    source_semantic = source_column[
                        "semantic_type"
                    ]

                    target_semantic = target_column[
                        "semantic_type"
                    ]

                    source_name_normalized = (
                        source_column_name.lower()
                    )

                    target_name_normalized = (
                        target_column_name.lower()
                    )

                    same_name = (
                        source_name_normalized
                        == target_name_normalized
                    )

                    compatible_semantic = (
                        source_semantic
                        == target_semantic
                    )

                    # Only report a relationship when
                    # the column meaning also supports it.
                    if not (
                        same_name
                        and compatible_semantic
                    ):
                        continue

                    relationships.append(
                        {
                            "source_file": source_name,
                            "source_column": source_column_name,
                            "target_file": target_name,
                            "target_column": target_column_name,
                            "relationship_type": "foreign_key",
                            "cardinality": "many_to_one",
                            "confidence": "high",
                        }
                    )

    return relationships
