
from typing import List
import traceback

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from app.services.profiling_service import profile_dataset
from app.services.query_generator import generate_search_query


router = APIRouter(
    prefix="/api/v1",
    tags=["Data Profiling"],
)


@router.post(
    "/profile",
    response_class=PlainTextResponse,
)
async def profile_data(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one CSV file is required.",
        )

    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Every uploaded file must have a filename.",
            )

        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail=f"Only CSV files are supported: {file.filename}",
            )

    try:
        uploaded_files = []

        for file in files:
            content = await file.read()

            uploaded_files.append(
                {
                    "filename": file.filename,
                    "content": content,
                }
            )

        # Step 1: Profile the uploaded CSV files.
        profiling_response = profile_dataset(uploaded_files)

        # Step 2: Convert the profiling JSON into descriptive plain text.
        text_response = generate_search_query(profiling_response)

        # Step 3: Return plain text instead of JSON.
        return PlainTextResponse(
            content=text_response,
            media_type="text/plain",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    except Exception as error:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
