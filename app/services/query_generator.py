
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
    """Reduce payload size without removing table or column definitions."""

    if isinstance(data, dict):
        result = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Exclude raw values that may contain PII.
            if key_lower in {"sample_values", "samples"}:
                continue

            # Retain only a few pattern examples.
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
    """Convert profiling JSON into readable text for RAG preparation."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    if not PROMPT_PATH.is_file():
        raise RuntimeError(f"Prompt file not found: {PROMPT_PATH}")

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8").strip()

    compact_response = compact_profile(profiling_response)

    profile_json = json.dumps(
        compact_response,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    prompt = f"{prompt_template}\n\n{profile_json}"

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
    )

    content = (response.choices[0].message.content or "").strip()

    if not content:
        raise RuntimeError("The Groq model returned an empty response.")

    return content
