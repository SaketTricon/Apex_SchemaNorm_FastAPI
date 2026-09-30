from pydantic import BaseModel


class SampleProfilingResponse(BaseModel):
    samples: list[dict[str, str | None]]