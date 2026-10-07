from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.profiling_service import profile_dataset


router = APIRouter(
    prefix="/api/v1",
    tags=["Data Profiling"],
)


@router.post("/profile")
async def profile_data(
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one CSV file must be uploaded.",
        )

    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file must have a filename.",
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

        return profile_dataset(uploaded_files)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
    