
import traceback
from typing import List

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import PlainTextResponse

from app.services.profiling_service import profile_dataset
from app.services.query_generator import (
    generate_search_query,
    generate_final_report,
)

from rag.vector_search import vector_search


router = APIRouter(
    prefix="/api/v1",
    tags=["Data Profiling"],
)


@router.post(
    "/profile",
    response_class=PlainTextResponse,
)
async def profile_data(
    request: Request,
    files: List[UploadFile] = File(...),
):

    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one CSV file is required.",
        )

    for file in files:

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Every uploaded file must have a filename.",
            )

        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail=f"Only CSV files are supported: {file.filename}",
            )

    try:
        # --------------------------------------------------
        # STEP 1: Generate profiling JSON
        # --------------------------------------------------

        print("\nSTEP 1: Profiling uploaded CSV files...")

        uploaded_files = []

        for file in files:
            content = await file.read()

            uploaded_files.append(
                {
                    "filename": file.filename,
                    "content": content,
                }
            )

        profiling_response = profile_dataset(uploaded_files)

        print("Profiling completed successfully.")

        # --------------------------------------------------
        # STEP 2: First LLM call - Generate RAG query
        # --------------------------------------------------

        print("\nSTEP 2: Generating RAG search query...")

        rag_query = generate_search_query(profiling_response)

        # print("\nGenerated RAG query:")
        # print(rag_query)

        # --------------------------------------------------
        # STEP 3: Vector search using preloaded index
        # --------------------------------------------------

        print("\nSTEP 3: Performing vector search...")

        rag_index = request.app.state.rag_index

        rag_results = vector_search(
            query=rag_query,
            index=rag_index,
            top_k=5,
        )

        if not rag_results:
            raise RuntimeError(
                "Vector search did not return any relevant knowledge."
            )

        # print(f"Retrieved {len(rag_results)} knowledge chunks.")

        # Build context with source information and content.
        rag_context = "\n\n".join(
            (
                f"Source: {result['source']}\n"
                f"Similarity score: {result['score']:.4f}\n"
                f"Content:\n{result['text']}"
            )
            for result in rag_results
        )

        # Print retrieved results for debugging.
        # print("\n" + "=" * 70)
        # print("RETRIEVED RAG CONTEXT")
        # print("=" * 70)

        # for position, result in enumerate(rag_results, start=1):
        #     print(f"\nResult {position}")
        #     print(f"Source: {result['source']}")
        #     print(f"Score: {result['score']:.4f}")
        #     print("-" * 70)
        #     print(result["text"])

        # --------------------------------------------------
        # STEP 4: Second LLM call - Generate final report
        # --------------------------------------------------

        print("\nSTEP 4: Generating final normalization report...")

        final_response = generate_final_report(
            profiling_response=profiling_response,
            rag_context=rag_context,
        )

        print("Final report generated successfully.")

        # --------------------------------------------------
        # STEP 5: Return final response to frontend
        # --------------------------------------------------

        return PlainTextResponse(
            content=final_response,
            media_type="text/plain",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    except Exception as error:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
