def build_data_quality_summary(
    files: list[dict],
) -> dict:

    high_null_columns = []
    duplicate_key_candidates = []

    for file_data in files:
        file_name = file_data["file_name"]

        candidate_primary_keys = {
            candidate["column"]
            for candidate in file_data[
                "candidate_primary_keys"
            ]
        }

        for column in file_data["column_profiles"]:

            statistics = column["statistics"]
            column_name = column["column_name"]

            # Detect columns with a high percentage of null values.
            if statistics["null_percentage"] >= 50:
                high_null_columns.append(
                    {
                        "file": file_name,
                        "column": column_name,
                        "null_percentage": statistics[
                            "null_percentage"
                        ],
                    }
                )

            # Only check duplicate values for columns that
            # have actually been identified as candidate
            # primary keys.
            if (
                column_name in candidate_primary_keys
                and statistics[
                    "duplicate_value_count"
                ] > 0
            ):
                duplicate_key_candidates.append(
                    {
                        "file": file_name,
                        "column": column_name,
                        "duplicate_value_count": statistics[
                            "duplicate_value_count"
                        ],
                    }
                )

    issues = []

    if high_null_columns:
        issues.append(
            "Columns with high null percentages were detected."
        )

    if duplicate_key_candidates:
        issues.append(
            "Potential duplicate values were detected "
            "in candidate primary key columns."
        )

    return {
        "files_with_high_null_columns": high_null_columns,
        "duplicate_key_candidates": duplicate_key_candidates,
        "potential_data_quality_issues": issues,
    }
