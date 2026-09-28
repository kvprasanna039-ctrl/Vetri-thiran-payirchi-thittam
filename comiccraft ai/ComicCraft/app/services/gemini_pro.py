import json

from google import genai
from google.genai import types

from app.config import get_settings
from app.models import ComicOutline, ComicStory


def _client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_story(
    outline: ComicOutline,
    character_name: str,
    tone: str,
    art_style: str,
) -> ComicStory:
    settings = get_settings()
    client = _client()

    prompt = f"""
Expand this comic outline into a polished panel-by-panel comic script.

Main character: {character_name}
Tone: {tone}
Art style: {art_style}

Outline:
{outline.model_dump_json(indent=2)}

Requirements:
- Preserve exact panel order and numbers.
- Keep character names and story facts consistent.
- Each panel needs a short caption, narration and dialogue where appropriate.
- Dialogue must be concise enough for a comic.
- Return structured JSON only.
"""

    response = client.models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=8000,
            response_mime_type="application/json",
            response_schema=ComicStory.model_json_schema(),
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty story.")

    try:
        return ComicStory.model_validate(json.loads(response.text))
    except Exception as exc:
        raise RuntimeError(f"Could not parse Gemini story: {exc}") from exc
