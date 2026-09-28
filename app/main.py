from fastapi import FastAPI

from app.api.routes.schema import router

app = FastAPI(
    title="Schema Profiling API",
)

app.include_router(router)


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
