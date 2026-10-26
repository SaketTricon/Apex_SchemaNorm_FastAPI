
import re
from typing import Any

from rank_bm25 import BM25Okapi

from rag.vector_search import vector_search


# --------------------------------------------------
# 1. TOKENIZATION
# --------------------------------------------------

def tokenize(text: str) -> list[str]:
    """Tokenize text for BM25 retrieval."""

    return re.findall(
        r"[a-zA-Z0-9_]+",
        text.lower(),
    )


# --------------------------------------------------
# 2. BUILD BM25 INDEX
# --------------------------------------------------

def build_bm25_index(index: dict[str, Any]) -> BM25Okapi:
    """
    Build BM25 index from the existing knowledge chunks.

    The BM25 index is built once during FastAPI startup.
    """

    chunks = index.get("chunks", [])

    if not chunks:
        raise ValueError(
            "Cannot build BM25 index: no knowledge chunks found."
        )

    corpus = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    return BM25Okapi(corpus)


# --------------------------------------------------
# 3. PARSE LLM-GENERATED QUERIES
# --------------------------------------------------

def parse_search_queries(response: str) -> dict[str, list[str]]:
    """
    Extract keyword and vector queries from the LLM response.

    Expected format:

    KEYWORD SEARCH QUERIES
    Query 1: ...

    VECTOR SEARCH QUERIES
    Query 1: ...
    """

    sections = {
        "keyword": [],
        "vector": [],
    }

    current_section = None

    for line in response.splitlines():

        line = line.strip()

        normalized = line.upper().rstrip(":").strip()

        if normalized == "KEYWORD SEARCH QUERIES":
            current_section = "keyword"
            continue

        if normalized == "VECTOR SEARCH QUERIES":
            current_section = "vector"
            continue

        if current_section is None:
            continue

        match = re.match(
            r"Query\s*\d+\s*:\s*(.+)",
            line,
            re.IGNORECASE,
        )

        if match:
            query = match.group(1).strip()

            if query and query.lower() != "none":
                sections[current_section].append(query)

    if not sections["keyword"] and not sections["vector"]:
        raise ValueError(
            "Could not parse keyword or vector queries "
            "from the LLM response."
        )

    return sections


# --------------------------------------------------
# 4. BM25 KEYWORD SEARCH
# --------------------------------------------------

def bm25_search(
    queries: list[str],
    index: dict[str, Any],
    bm25_index: BM25Okapi,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve knowledge chunks using BM25 keyword matching.

    Each keyword query is searched independently.
    Duplicate chunks are removed.
    """

    chunks = index["chunks"]

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    results = {}

    for query in queries:

        tokens = tokenize(query)

        if not tokens:
            continue

        scores = bm25_index.get_scores(tokens)

        ranked_positions = sorted(
            range(len(scores)),
            key=lambda position: scores[position],
            reverse=True,
        )

        added = 0

        for position in ranked_positions:

            score = float(scores[position])

            # Ignore chunks with no keyword relevance.
            if score <= 0:
                break

            chunk = chunks[position]

            chunk_key = (
                chunk["source"],
                chunk["id"],
            )

            if chunk_key not in results:

                results[chunk_key] = {
                    "id": chunk["id"],
                    "source": chunk["source"],
                    "text": chunk["text"],
                    "bm25_score": score,
                }

            else:
                results[chunk_key]["bm25_score"] = max(
                    results[chunk_key]["bm25_score"],
                    score,
                )

            added += 1

            if added >= top_k:
                break

    return sorted(
        results.values(),
        key=lambda item: item["bm25_score"],
        reverse=True,
    )


# --------------------------------------------------
# 5. HYBRID SEARCH USING RRF
# --------------------------------------------------

def hybrid_search(
    queries: dict[str, list[str]],
    index: dict[str, Any],
    bm25_index: BM25Okapi,
    top_k: int = 5,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """
    Combine BM25 and vector retrieval using
    Reciprocal Rank Fusion (RRF).

    Workflow:
        1. Execute BM25 searches.
        2. Execute vector searches.
        3. Combine rankings using RRF.
        4. Deduplicate chunks.
        5. Return the highest-ranked chunks.
    """

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if rrf_k <= 0:
        raise ValueError("rrf_k must be greater than zero.")

    keyword_queries = queries.get("keyword", [])
    vector_queries = queries.get("vector", [])

    if not keyword_queries and not vector_queries:
        raise ValueError("No search queries were supplied.")

    fused_results = {}

    # ----------------------------------------------
    # RRF RESULT MERGING
    # ----------------------------------------------

    def add_ranked_results(
        results: list[dict[str, Any]],
        method: str,
    ) -> None:

        for rank, result in enumerate(results, start=1):

            chunk_key = (
                result["source"],
                result["id"],
            )

            if chunk_key not in fused_results:

                fused_results[chunk_key] = {
                    "id": result["id"],
                    "source": result["source"],
                    "text": result["text"],
                    "rrf_score": 0.0,
                    "retrieval_methods": [],
                }

            fused = fused_results[chunk_key]

            # Reciprocal Rank Fusion
            fused["rrf_score"] += (
                1.0 / (rrf_k + rank)
            )

            if method not in fused["retrieval_methods"]:
                fused["retrieval_methods"].append(method)

            # Preserve original retrieval scores.
            score_key = f"{method}_score"

            raw_score = result.get(
                "score" if method == "vector" else score_key
            )

            if raw_score is not None:

                fused[score_key] = max(
                    fused.get(
                        score_key,
                        float("-inf"),
                    ),
                    float(raw_score),
                )

    # ----------------------------------------------
    # BM25 RETRIEVAL
    # ----------------------------------------------

    for query in keyword_queries:

        results = bm25_search(
            queries=[query],
            index=index,
            bm25_index=bm25_index,
            top_k=top_k,
        )

        add_ranked_results(
            results=results,
            method="bm25",
        )

    # ----------------------------------------------
    # VECTOR RETRIEVAL
    # ----------------------------------------------

    for query in vector_queries:

        results = vector_search(
            query=query,
            index=index,
            top_k=top_k,
        )

        add_ranked_results(
            results=results,
            method="vector",
        )

    # ----------------------------------------------
    # FINAL RANKING
    # ----------------------------------------------

    ranked_results = sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return ranked_results[:top_k]
