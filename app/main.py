from fastapi import FastAPI

app = FastAPI(
    title="APEX Schema Normalization API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
