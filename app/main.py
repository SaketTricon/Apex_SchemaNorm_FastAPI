from fastapi import FastAPI

from app.api.routes.schema import router

from app.api.routes.profiling import router as profiling_router


app = FastAPI(
    title="Schema Profiling API",
)

app.include_router(router)
app.include_router(profiling_router)


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
