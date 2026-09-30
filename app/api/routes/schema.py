from pathlib import Path

import pandas as pd

from fastapi import APIRouter

from app.core.database import connect_to_database
from app.services.schema_profiler import SchemaProfiler


router = APIRouter(
    prefix="/api/v1/schema",
    tags=["Schema Profiling"],
)


CSV_PATH = Path(
    "data/vendor_dump.csv"
)


@router.post("/profile")
def profile_schema(
    host: str | None = None,
    port: int | None = None,
    database: str | None = None,
    username: str | None = None,
    password: str | None = None,
    schema_name: str = "public",
):

    profiler = SchemaProfiler()

    # ---------------------------------------------------------
    # DATABASE MODE
    # ---------------------------------------------------------

    if all(
        [
            host,
            port,
            database,
            username,
            password,
        ]
    ):

        connection = connect_to_database(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
        )

        try:

            profiler.connection = connection

            return profiler.profile_database(
                schema_name=schema_name
            )

        finally:

            connection.close()

    # ---------------------------------------------------------
    # CSV MODE
    # ---------------------------------------------------------

    dataframe = pd.read_csv(
        CSV_PATH,
        dtype=str,
    )

    return profiler.profile_csv(
        dataframe
    )
