import csv
import io

from app.services.data_quality_profiler import (
    build_data_quality_summary,
)
from app.services.relationship_profiler import (
    find_candidate_primary_keys,
    find_foreign_keys,
)
from app.services.sample_profiler import (
    profile_column_patterns,
)
from app.services.schema_profiler import (
    profile_csv_schema,
)
from app.services.statistical_profiler import (
    profile_statistics,
)


def read_csv(
    content: bytes,
) -> list[dict]:

    text = content.decode(
        "utf-8-sig"
    )

    reader = csv.DictReader(
        io.StringIO(text)
    )

    if not reader.fieldnames:
        raise ValueError(
            "CSV does not contain headers."
        )

    rows = list(reader)

    if not rows:
        raise ValueError(
            "CSV does not contain data."
        )

    return rows


def profile_dataset(
    uploaded_files: list[dict],
) -> dict:

    file_results = []

    total_rows = 0
    total_columns = 0

    for uploaded_file in uploaded_files:

        filename = uploaded_file[
            "filename"
        ]

        content = uploaded_file[
            "content"
        ]

        rows = read_csv(content)

        columns = list(
            rows[0].keys()
        )

        schema = profile_csv_schema(
            rows,
            columns,
        )

        statistics = profile_statistics(
            rows,
            schema["columns"],
        )

        candidate_primary_keys = (
            find_candidate_primary_keys(
                rows,
                schema["columns"],
            )
        )

        column_profiles = []

        for schema_column in schema[
            "columns"
        ]:

            column_name = schema_column[
                "column_name"
            ]

            column_statistics = next(
                item["statistics"]
                for item in statistics
                if item["column_name"]
                == column_name
            )

            pattern_data = (
                profile_column_patterns(
                    rows,
                    column_name,
                )
            )

            key_analysis = next(
                (
                    candidate
                    for candidate
                    in candidate_primary_keys
                    if candidate["column"]
                    == column_name
                ),
                None,
            )

            if key_analysis is None:
                key_analysis = {
                    "candidate_primary_key": False,
                    "uniqueness_percentage": (
                        column_statistics[
                            "distinct_percentage"
                        ]
                    ),
                }

            column_profiles.append(
                {
                    "column_name": column_name,
                    "position": schema_column[
                        "position"
                    ],
                    "inferred_data_type": (
                        schema_column[
                            "inferred_data_type"
                        ]
                    ),
                    "semantic_type": (
                        schema_column[
                            "semantic_type"
                        ]
                    ),
                    "nullable": schema_column[
                        "nullable"
                    ],
                    "statistics": (
                        column_statistics
                    ),
                    "patterns": (
                        pattern_data[
                            "patterns"
                        ]
                    ),
                    "sample_values": (
                        pattern_data[
                            "sample_values"
                        ]
                    ),
                    "key_analysis": (
                        key_analysis
                    ),
                }
            )

        table_level_analysis = {
            "candidate_primary_keys": [
                candidate["column"]
                for candidate
                in candidate_primary_keys
            ],
            "candidate_business_keys": [],
            "possible_duplicate_columns": [],
            "possible_audit_columns": [
                column["column_name"]
                for column in schema[
                    "columns"
                ]
                if column["semantic_type"]
                == "timestamp"
            ],
            "possible_pii_columns": [
                column["column_name"]
                for column in schema[
                    "columns"
                ]
                if column["semantic_type"]
                in {
                    "email",
                    "phone_number",
                    "person_name",
                    "address",
                }
            ],
        }

        file_results.append(
            {
                "file_name": filename,
                "table_name": filename.rsplit(
                    ".",
                    1,
                )[0],
                "rows": rows,
                "schema": schema,
                "candidate_primary_keys": (
                    candidate_primary_keys
                ),
                "column_profiles": (
                    column_profiles
                ),
                "file_statistics": {
                    "row_count": len(rows),
                    "column_count": len(
                        columns
                    ),
                    "file_size_bytes": len(
                        content
                    ),
                },
                "table_level_analysis": (
                    table_level_analysis
                ),
            }
        )

        total_rows += len(rows)
        total_columns += len(columns)

    cross_file_relationships = (
        find_foreign_keys(
            file_results
        )
    )

    data_quality_summary = (
        build_data_quality_summary(
            file_results
        )
    )

    final_files = []

    for file_data in file_results:

        final_files.append(
            {
                "file_name": file_data[
                    "file_name"
                ],
                "table_name": file_data[
                    "table_name"
                ],
                "file_statistics": file_data[
                    "file_statistics"
                ],
                "schema": {
                    "columns": file_data[
                        "column_profiles"
                    ]
                },
                "table_level_analysis": (
                    file_data[
                        "table_level_analysis"
                    ]
                ),
            }
        )

    return {
        "dataset_summary": {
            "file_count": len(
                uploaded_files
            ),
            "total_rows": total_rows,
            "total_columns": total_columns,
            "files": [
                {
                    "file_name": file[
                        "file_name"
                    ],
                    "row_count": file[
                        "file_statistics"
                    ]["row_count"],
                    "column_count": file[
                        "file_statistics"
                    ]["column_count"],
                }
                for file in file_results
            ],
        },
        "files": final_files,
        "cross_file_relationships": (
            cross_file_relationships
        ),
        "data_quality_summary": (
            data_quality_summary
        ),
    }
