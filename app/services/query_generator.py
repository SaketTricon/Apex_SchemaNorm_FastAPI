
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

MODEL_NAME = "openai/gpt-oss-120b"

PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"

QUERY_PROMPT_PATH = PROMPT_DIR / "rag_query_generation.txt"
FINAL_PROMPT_PATH = PROMPT_DIR / "final_prompt.txt"


def get_groq_client(api_key_env: str) -> Groq:
    """Create a Groq client using the specified environment variable."""

    api_key = os.getenv(api_key_env)

    if not api_key:
        raise RuntimeError(
            f"{api_key_env} is not configured in the .env file."
        )

    return Groq(api_key=api_key)


def compact_profile(data):
    """Remove raw sample values and reduce unnecessary payload size."""

    if isinstance(data, dict):
        result = {}

        for key, value in data.items():
            key_lower = key.lower()

            if key_lower in {"sample_values", "samples"}:
                continue

            if key_lower in {"patterns", "pattern_examples"}:
                if isinstance(value, list):
                    result[key] = value[:2]
                elif isinstance(value, dict):
                    result[key] = compact_profile(value)
                else:
                    result[key] = value

                continue

            result[key] = compact_profile(value)

        return result

    if isinstance(data, list):
        return [compact_profile(item) for item in data]

    return data


def generate_search_query(profiling_response: dict) -> str:
    """Generate BM25 and vector search queries from profiling JSON."""

    if not QUERY_PROMPT_PATH.is_file():
        raise RuntimeError(
            f"RAG query prompt not found: {QUERY_PROMPT_PATH}"
        )

    prompt_template = QUERY_PROMPT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    profile_json = json.dumps(
        compact_profile(profiling_response),
        ensure_ascii=False,
        indent=2,
    )

    prompt = prompt_template.replace(
        "{{PROFILE_JSON}}",
        profile_json,
    )

    client = get_groq_client("GROQ_QUERY_API_KEY")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    content = (
        response.choices[0].message.content or ""
    ).strip()

    if not content:
        raise RuntimeError(
            "The RAG query generation returned an empty response."
        )

    return content

def generate_final_report(
    profiling_response: dict,
    rag_context: str,
) -> str:
    """Second LLM call: generate the final normalized schema JSON."""

    if not FINAL_PROMPT_PATH.is_file():
        raise RuntimeError(f"Final prompt not found: {FINAL_PROMPT_PATH}")

    if not rag_context.strip():
        raise ValueError("RAG context is empty.")

    # Load final prompt template
    prompt_template = FINAL_PROMPT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    # Prepare profile JSON
    profile_json = json.dumps(
        compact_profile(profiling_response),
        ensure_ascii=False,
        indent=2,
    )

    # Inject dynamic inputs into the prompt
    final_prompt = (
        prompt_template
        .replace("{{PROFILE_JSON}}", profile_json)
        .replace("{{RAG_CONTEXT}}", rag_context)
    )

    # Second LLM call
    client = get_groq_client("GROQ_FINAL_API_KEY")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": final_prompt,
            }
        ],
        temperature=0.1,
    )

    content = (
        response.choices[0].message.content or ""
    ).strip()

    if not content:
        raise RuntimeError(
            "The final report generation returned an empty response."
        )

    return content