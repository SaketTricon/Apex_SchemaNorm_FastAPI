import pickle
from pathlib import Path
from typing import Any

import numpy as np

from rag.chunker import chunk_documents
from rag.embeddings import MODEL_NAME, create_embeddings
from rag.loader import load_documents


def build_index(
    knowledge_dir: str | Path,
    output_file: str | Path,
    chunk_size: int = 500,
) -> dict[str, Any]:
    documents = load_documents(knowledge_dir)
    chunks = chunk_documents(documents, chunk_size=chunk_size)
    if not chunks:
        raise ValueError(f"No Markdown content found under {knowledge_dir}")

    embeddings = create_embeddings([chunk["text"] for chunk in chunks])
    index = {
        "model_name": MODEL_NAME,
        "chunks": chunks,
        "embeddings": embeddings,
    }

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as output:
        pickle.dump(index, output, protocol=pickle.HIGHEST_PROTOCOL)

    return index


def load_index(index_file: str | Path) -> dict[str, Any]:
    with Path(index_file).open("rb") as source:
        index = pickle.load(source)

    if not isinstance(index, dict) or not {"chunks", "embeddings"}.issubset(index):
        raise ValueError(f"Invalid RAG index: {index_file}")

    chunks = index["chunks"]
    embeddings = np.asarray(index["embeddings"])
    if embeddings.ndim != 2 or len(chunks) != embeddings.shape[0]:
        raise ValueError(f"RAG index has inconsistent chunks and embeddings: {index_file}")
    index["embeddings"] = embeddings
    return index
