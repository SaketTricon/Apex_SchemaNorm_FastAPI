from fastapi import FastAPI

from app.api.routes.profiling import router as profiling_router


app = FastAPI(
    title="Vendor Data Profiling API",
    version="1.0.0",
)

app.include_router(profiling_router)


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
