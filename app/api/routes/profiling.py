from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.database import connect_to_database
from app.services.profiling_service import (
    profile_csv,
    profile_postgres,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Data Profiling"],
)


class ProfilingRequest(BaseModel):

    host: Optional[str] = None
    port: Optional[int] = 5432
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    schema_name: str = "public"
    table_name: str = "vendor_dump"


@router.post("/profile")
def profile_data(
    request: ProfilingRequest,
):

    credentials = [
        request.host,
        request.database,
        request.username,
        request.password,
    ]

    credentials_provided = any(
        value is not None
        for value in credentials
    )

    credentials_complete = all(
        value is not None
        for value in credentials
    )

    # --------------------------------------------------
    # DATABASE MODE
    # --------------------------------------------------

    if credentials_provided:

        if not credentials_complete:
            raise HTTPException(
                status_code=400,
                detail=(
                    "host, database, username and "
                    "password must all be provided."
                ),
            )

        connection = None

        try:

            connection = connect_to_database(
                host=request.host,
                port=request.port or 5432,
                database=request.database,
                username=request.username,
                password=request.password,
            )

            return profile_postgres(
                connection=connection,
                schema_name=request.schema_name,
                table_name=request.table_name,
            )

        except Exception as error:

            raise HTTPException(
                status_code=500,
                detail=str(error),
            )

        finally:

            if connection:
                connection.close()

    # --------------------------------------------------
    # CSV MODE
    # --------------------------------------------------

    try:

        return profile_csv()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
