import io

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.models.sample_profiling import SampleProfilingResponse
from app.services.sample_profiling import SampleFileError, sample_csv_records

router = APIRouter(prefix="/profiling", tags=["profiling"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/samples", response_model=SampleProfilingResponse)
async def create_samples(
    file: UploadFile = File(...),
    sample_size: int = Query(default=2, ge=1, le=100),
) -> SampleProfilingResponse:
    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="CSV file exceeds the 10 MiB limit")

    text_file = io.TextIOWrapper(file.file, encoding="utf-8-sig", newline="")
    try:
        samples = sample_csv_records(text_file, sample_size)
    except (SampleFileError, UnicodeDecodeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        text_file.detach()

    return SampleProfilingResponse(samples=samples)