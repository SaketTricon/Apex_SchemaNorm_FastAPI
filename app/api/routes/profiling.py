
import json
import traceback
from typing import List

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from app.services.profiling_service import profile_dataset
from app.services.profile_optimizer import optimize_profile_json

from app.services.query_generator import (
    generate_search_query,
    generate_final_report,
)

from rag.hybrid_search import (
    parse_search_queries,
    hybrid_search,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Data Profiling"],
)


@router.post(
    "/profile",
    response_class=JSONResponse,
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
        # STEP 1: Profile uploaded files
        print("\nSTEP 1: Profiling uploaded CSV files...")

        uploaded_files = []

        for file in files:
            content = await file.read()

            uploaded_files.append({
                "filename": file.filename,
                "content": content,
            })

        profiling_response = profile_dataset(uploaded_files)

        print("Profiling completed successfully.")

        # STEP 2: Optimize profiling JSON
        print("\nSTEP 2: Optimizing profiling JSON...")

        optimized_profile = optimize_profile_json(
            profiling_response
        )

        print("Profile JSON optimized successfully.")
        print(
            f"Original profile size: "
            f"{len(str(profiling_response))} characters"
        )
        print(
            f"Optimized profile size: "
            f"{len(optimized_profile)} characters"
        )

        # STEP 3: Generate BM25 and vector queries
        print("\nSTEP 3: Generating hybrid search queries...")

        generated_queries = generate_search_query(
            optimized_profile
        )

        # print("\nGenerated search queries:")
        # print(generated_queries)

        # Parse the LLM response
        search_queries = parse_search_queries(
            generated_queries
        )

        # print("\nParsed keyword queries:")
        # print(search_queries["keyword"])

        # print("\nParsed vector queries:")
        # print(search_queries["vector"])

        # STEP 4: Perform hybrid search
        print("\nSTEP 4: Performing hybrid retrieval...")

        rag_index = request.app.state.rag_index
        bm25_index = request.app.state.bm25_index

        rag_results = hybrid_search(
            queries=search_queries,
            index=rag_index,
            bm25_index=bm25_index,
            top_k=5,
        )

        if not rag_results:
            raise RuntimeError(
                "Hybrid search did not return any relevant knowledge."
            )

        print(f"\nRetrieved {len(rag_results)} knowledge chunks.")

        # Prepare context for final LLM
        rag_context = "\n\n".join(
            (
                f"Source: {result['source']}\n"
                f"Retrieval methods: {', '.join(result['retrieval_methods'])}\n"
                f"RRF score: {result['rrf_score']:.6f}\n"
                f"Content:\n{result['text']}"
            )
            for result in rag_results
        )

        # # Log retrieval results
        # print("\n" + "=" * 70)
        # print("HYBRID SEARCH RESULTS")
        # print("=" * 70)

        # for position, result in enumerate(rag_results, start=1):
        #     print(f"\nResult {position}")
        #     print(f"Source: {result['source']}")
        #     print(f"Methods: {result['retrieval_methods']}")
        #     print(f"RRF score: {result['rrf_score']:.6f}")

        #     if "bm25_score" in result:
        #         print(f"BM25 score: {result['bm25_score']:.4f}")

        #     if "vector_score" in result:
        #         print(f"Vector score: {result['vector_score']:.4f}")

        #     print("-" * 70)
        #     print(result["text"])

        # STEP 5: Generate final normalization report
        print("\nSTEP 5: Generating final normalization report...")

        final_response = generate_final_report(
            profiling_response=profiling_response,
            rag_context=rag_context,
        )

        try:
            analysis = json.loads(final_response)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                "The final report was not valid JSON. Please retry the analysis."
            ) from error

        required_sections = {"tables", "mappings", "findings"}
        if (
            not isinstance(analysis, dict)
            or set(analysis) != required_sections
            or any(not isinstance(analysis[section], list) for section in required_sections)
        ):
            raise RuntimeError(
                "The final report must contain tables, mappings, and findings arrays."
            )

        print("Final report generated successfully.")

        return JSONResponse(content=analysis)

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
