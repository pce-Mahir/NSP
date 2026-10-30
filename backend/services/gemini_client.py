import logging
import os
import time
from typing import Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError

from backend.core.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger('ats_resume_scorer')

_client: Optional[genai.Client] = None

FALLBACK_MODELS = [
    GEMINI_MODEL,
    'gemini-3.5-flash',
    'gemini-3.5-flash-lite',
    'gemini-3.8-flash',
]


def gemini_configured() -> bool:
    return bool(GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to .env to enable Gemini parsing "
                "and career guidance."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def generate_text(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.2,
    max_output_tokens: int = 8192,
    json_mode: bool = False,
) -> str:
    client = get_client()
    config_kwargs = {
        'system_instruction': system_prompt,
        'temperature': temperature,
        'max_output_tokens': max_output_tokens,
    }
    if json_mode:
        config_kwargs['response_mime_type'] = 'application/json'

    # Try configured model, and fall back to alternative models if temporary 503 / high demand occurs
    last_error = None
    seen_models = set()
    models_to_try = []
    for m in [GEMINI_MODEL, 'gemini-3.5-flash', 'gemini-3.5-flash-lite']:
        if m and m not in seen_models:
            seen_models.add(m)
            models_to_try.append(m)

    for attempt_model in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=attempt_model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
                text = (response.text or '').strip()
                if not text:
                    raise ValueError('Gemini returned an empty response')
                return text
            except Exception as exc:
                last_error = exc
                err_str = str(exc)
                if '503' in err_str or '429' in err_str or 'high demand' in err_str:
                    logger.warning(
                        f"Gemini {attempt_model} hit high demand (attempt {attempt+1}). Retrying / falling back..."
                    )
                    time.sleep(1.0)
                    continue
                else:
                    # Model not found or permanent error, try next model in fallback list
                    break

    if last_error:
        raise last_error
    raise ValueError('Gemini generation failed')
