from typing import Any

import numpy as np

from rag.embeddings import create_embeddings


def vector_search(
    query: str,
    index: dict[str, Any],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("query must not be empty")
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    chunks = index["chunks"]
    embeddings = np.asarray(index["embeddings"], dtype=np.float32)
    if embeddings.ndim != 2 or len(chunks) != embeddings.shape[0]:
        raise ValueError("Index has inconsistent chunks and embeddings")
    if not chunks:
        return []

    query_embedding = create_embeddings([query])[0]
    if embeddings.shape[1] != query_embedding.shape[0]:
        raise ValueError("Query embedding dimension does not match the index")

    scores = embeddings @ query_embedding
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [
        {
            "id": chunks[position]["id"],
            "source": chunks[position]["source"],
            "text": chunks[position]["text"],
            "score": float(scores[position]),
        }
        for position in top_indices
    ]
