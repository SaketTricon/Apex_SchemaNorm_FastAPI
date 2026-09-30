import re

import pandas as pd


class SchemaProfiler:

    def __init__(self, connection=None):
        self.connection = connection

    # ---------------------------------------------------------
    # CSV
    # ---------------------------------------------------------

    def profile_csv(self, dataframe):

        columns = []

        for column in dataframe.columns:

            data_type = self._infer_type(
                dataframe[column]
            )

            columns.append(
                {
                    "name": column,
                    "data_type": data_type,
                    "nullable": bool(
                        dataframe[column].isna().any()
                    ),
                    "classification": self._classify(
                        column,
                        data_type,
                    ),
                }
            )

        return self._build_profile(
            columns=columns,
            table_name="vendor_dump",
            source_type="csv",
        )

    # ---------------------------------------------------------
    # POSTGRESQL
    # ---------------------------------------------------------

    def profile_database(
        self,
        schema_name="public",
    ):

        tables = self._get_tables(
            schema_name
        )

        profiles = []

        for table in tables:

            columns = self._get_columns(
                schema_name,
                table,
            )

            primary_keys = self._get_primary_keys(
                schema_name,
                table,
            )

            foreign_keys = self._get_foreign_keys(
                schema_name,
                table,
            )

            for column in columns:

                column["primary_key"] = (
                    column["name"]
                    in primary_keys
                )

                column["foreign_key"] = (
                    column["name"]
                    in foreign_keys
                )

                column["classification"] = (
                    self._classify(
                        column["name"],
                        column["data_type"],
                    )
                )

            profiles.append(
                {
                    "schema_name": schema_name,
                    "table_name": table,
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys,
                }
            )

        return {
            "source_type": "postgresql",
            "tables": profiles,
        }

    def _get_tables(
        self,
        schema_name,
    ):

        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (schema_name,),
            )

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    def _get_columns(
        self,
        schema_name,
        table_name,
    ):

        query = """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s
            AND table_name = %s
            ORDER BY ordinal_position
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    schema_name,
                    table_name,
                ),
            )

            rows = cursor.fetchall()

        return [
            {
                "name": row[0],
                "data_type": row[1],
                "nullable": row[2] == "YES",
                "primary_key": False,
                "foreign_key": False,
                "classification": [],
            }
            for row in rows
        ]

    def _get_primary_keys(
        self,
        schema_name,
        table_name,
    ):

        query = """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = %s
            AND tc.table_name = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    schema_name,
                    table_name,
                ),
            )

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    def _get_foreign_keys(
        self,
        schema_name,
        table_name,
    ):

        query = """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = %s
            AND tc.table_name = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    schema_name,
                    table_name,
                ),
            )

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    # ---------------------------------------------------------
    # TYPE INFERENCE
    # ---------------------------------------------------------

    def _infer_type(self, series):

        values = (
            series.dropna()
            .astype(str)
            .str.strip()
        )

        if values.empty:
            return "unknown"

        if values.str.lower().isin(
            {
                "true",
                "false",
            }
        ).all():
            return "boolean"

        numeric = pd.to_numeric(
            values,
            errors="coerce",
        )

        if numeric.notna().all():
            return "numeric"

        dates = pd.to_datetime(
            values,
            errors="coerce",
        )

        if dates.notna().all():
            return "date_time"

        return "string"

    # ---------------------------------------------------------
    # CLASSIFICATION
    # ---------------------------------------------------------

    def _classify(
        self,
        name,
        data_type,
    ):

        result = []

        name = name.lower()

        if data_type in {
            "numeric",
            "integer",
            "bigint",
            "decimal",
            "numeric",
        }:
            result.append("numeric")

        if data_type in {
            "date",
            "datetime",
            "date_time",
            "timestamp without time zone",
            "timestamp with time zone",
        }:
            result.append("date_time")

        if data_type in {
            "boolean",
        }:
            result.append("boolean")

        if re.search(
            r"(^|_)(id|key|code|identifier|uuid|ref)($|_)",
            name,
        ):
            result.append("identifier_like")

        return result

    # ---------------------------------------------------------
    # FINAL PROFILE
    # ---------------------------------------------------------

    def _build_profile(
        self,
        columns,
        table_name,
        source_type,
    ):

        return {
            "source_type": source_type,
            "table_name": table_name,
            "column_count": len(columns),
            "columns": columns,
            "identifier_candidates": [
                column["name"]
                for column in columns
                if "identifier_like"
                in column["classification"]
            ],
            "date_columns": [
                column["name"]
                for column in columns
                if "date_time"
                in column["classification"]
            ],
            "boolean_columns": [
                column["name"]
                for column in columns
                if "boolean"
                in column["classification"]
            ],
            "numeric_columns": [
                column["name"]
                for column in columns
                if "numeric"
                in column["classification"]
            ],
        }
