
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.profiling import router as profiling_router
from rag.embeddings import load_embedding_model
from rag.index import load_index


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = PROJECT_ROOT / "rag" / "data" / "knowledge_index.pkl"


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("\nInitializing RAG resources...")

    # Load embedding model weights.
    print("Loading embedding model...")
    app.state.embedding_model = load_embedding_model()
    print("Embedding model ready.")

    # Load prebuilt knowledge index.
    print("Loading knowledge index...")

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge index not found: {INDEX_PATH}. "
            "Run python -m rag.scripts.build_knowledge_index first."
        )

    app.state.rag_index = load_index(INDEX_PATH)

    # print(
    #     f"Knowledge index loaded: "
    #     f"{len(app.state.rag_index['chunks'])} chunks."
    # )

    print("RAG initialization completed.\n")

    yield

    print("Application shutting down.")


app = FastAPI(
    title="Vendor Data Profiling API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(profiling_router)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "embedding_model_loaded": hasattr(app.state, "embedding_model"),
        "rag_index_loaded": hasattr(app.state, "rag_index"),
    }


app.mount(
    "/",
    StaticFiles(
        directory=PROJECT_ROOT / "ui",
        html=True,
    ),
    name="ui",
)
