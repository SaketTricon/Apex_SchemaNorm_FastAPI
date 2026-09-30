from fastapi import FastAPI

from app.api.routes.profiling import router as profiling_router

app = FastAPI(
    title="APEX Schema Normalization API",
    version="0.1.0",
)

app.include_router(profiling_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
