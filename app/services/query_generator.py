
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"

PROMPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "prompts"
    / "rag_query_generation.txt"
)


def compact_profile(data):
    """Remove raw samples and limit pattern examples to reduce token usage."""

    if isinstance(data, dict):
        result = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Remove raw sample values to reduce size and protect PII.
            if key_lower in {"sample_values", "samples"}:
                continue

            # Keep at most three pattern examples.
            if key_lower in {"patterns", "pattern_examples"}:
                if isinstance(value, list):
                    result[key] = value[:3]
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


def generate_search_query(profiling_response: dict) -> dict:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    if not PROMPT_PATH.is_file():
        raise RuntimeError(f"Prompt file not found: {PROMPT_PATH}")

    # Load fixed instructions.
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    # Reduce the profiling payload before sending it to Groq.
    compact_response = compact_profile(profiling_response)

    profile_json = json.dumps(
        compact_response,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    prompt = (
        f"{prompt_template}\n\n"
        f"VENDOR PROFILING JSON:\n{profile_json}\n"
    )

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = (response.choices[0].message.content or "").strip()

    if not content:
        raise RuntimeError("The Groq model returned an empty response.")

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "The Groq model did not return valid JSON."
        ) from exc

    if not isinstance(result, dict):
        raise RuntimeError("The Groq response must be a JSON object.")

    required_keys = {
        "dataset_context",
        "keyword_queries",
        "vector_queries",
        "relationship_queries",
        "mapping_queries",
        "schema_queries",
    }

    missing_keys = required_keys - result.keys()

    if missing_keys:
        raise RuntimeError(
            "The Groq response is missing required fields: "
            + ", ".join(sorted(missing_keys))
        )

    return result
