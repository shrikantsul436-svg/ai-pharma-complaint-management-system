"""
Thin wrapper around the Groq SDK so the rest of the code never touches
the SDK directly. Two model tiers are used on purpose:

- GROQ_EXTRACTION_MODEL (gemma2-9b-it): fast + cheap, good for structured
  field extraction from a single document.
- GROQ_REASONING_MODEL (llama-3.3-70b-versatile): used for the heavier
  reasoning steps (root cause / CAPA suggestions, chat follow-ups) where
  more context and better instruction-following pays off.
"""
import json
from groq import Groq

from app.config import settings

_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


def _require_client():
    if _client is None:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to backend/.env - see .env.example."
        )
    return _client


def call_groq_json(system_prompt: str, user_prompt: str, model: str, temperature: float = 0.1) -> dict:
    """
    Calls Groq's chat completion endpoint and expects a JSON object back.
    We ask the model for JSON explicitly and also set response_format,
    which both gemma2-9b-it and llama-3.3-70b-versatile support on Groq.
    """
    client = _require_client()
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Defensive fallback in case the model wraps JSON in prose/backticks
        cleaned = content.strip().strip("`")
        cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned
        return json.loads(cleaned)


def call_groq_text(system_prompt: str, user_prompt: str, model: str, temperature: float = 0.3) -> str:
    client = _require_client()
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content
