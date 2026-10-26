
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"
PROMPT_DIR = PROJECT_ROOT / "prompts"

QUERY_PROMPT_PATH = PROMPT_DIR / "rag_query_generation.txt"
FINAL_PROMPT_PATH = PROMPT_DIR / "final_prompt.txt"

MODEL_NAME = "openai/gpt-oss-120b"

load_dotenv(ENV_PATH)


def get_groq_client(api_key_env: str) -> Groq:
    api_key = os.getenv(api_key_env)

    if not api_key:
        raise RuntimeError(
            f"{api_key_env} is not configured in the .env file."
        )

    return Groq(api_key=api_key)


def compact_profile(data):
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


def prepare_profile_json(profiling_response) -> str:
    """
    Accept either a JSON string or a Python dictionary.
    """

    if isinstance(profiling_response, str):
        # Validate that the string contains valid JSON.
        json.loads(profiling_response)
        return profiling_response

    return json.dumps(
        compact_profile(profiling_response),
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def generate_search_query(profiling_response) -> str:
    if not QUERY_PROMPT_PATH.is_file():
        raise RuntimeError(
            f"RAG query prompt not found: {QUERY_PROMPT_PATH}"
        )

    profile_json = prepare_profile_json(profiling_response)

    prompt_template = QUERY_PROMPT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    prompt = prompt_template.replace(
        "{{PROFILE_JSON}}",
        profile_json,
    )

    client = get_groq_client("GROQ_QUERY_API_KEY")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
    )
    print("first is done")

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

    if not FINAL_PROMPT_PATH.is_file():
        raise RuntimeError(
            f"Final prompt not found: {FINAL_PROMPT_PATH}"
        )

    if not rag_context.strip():
        raise ValueError("RAG context is empty.")

    profile_json = prepare_profile_json(profiling_response)

    prompt_template = FINAL_PROMPT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    final_prompt = (
        prompt_template
        .replace("{{PROFILE_JSON}}", profile_json)
        .replace("{{RAG_CONTEXT}}", rag_context)
    )

    client = get_groq_client("GROQ_FINAL_API_KEY")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    print("second id done")
    content = (
        response.choices[0].message.content or ""
    ).strip()

    if not content:
        raise RuntimeError(
            "The final report generation returned an empty response."
        )

    # Validate the returned JSON.
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "The final report model returned invalid JSON."
        ) from exc

    return content
