# Groq API utility (call, parse, retry)

import asyncio
import json

from groq import AsyncGroq

from app.config import settings

_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"


class LLMCallError(Exception):
    """Raised when an LLM call fails to produce valid JSON after retrying."""


async def call_llm_json(prompt: str) -> dict:
    """Call the LLM with a prompt that must return JSON, parse the response, retry once on failure.

    Raises LLMCallError if both the initial call and the single retry fail
    (API error or unparseable JSON), so callers can fail the session step
    with a clear message.
    """
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = await _client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == 0:
                await asyncio.sleep(1)
                continue

    raise LLMCallError(f"LLM call failed after retry: {last_error}") from last_error
