import json

from google import genai
from google.genai import types

from app.config import get_settings
from app.models import ComicOutline


def _client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:
    settings = get_settings()
    client = _client()

    prompt = f"""
Create a coherent {settings.comic_panels}-panel comic outline.

User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Requirements:
- Return exactly {settings.comic_panels} panels.
- Keep the same main character and visual identity across all panels.
- Give every panel a clear title.
- scene_description should explain action, environment and emotional beat.
- image_prompt should be production-ready for a text-to-image model.
- Do not include markdown fences.
"""

    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=5000,
            response_mime_type="application/json",
            response_schema=ComicOutline.model_json_schema(),
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty outline.")

    try:
        outline = ComicOutline.model_validate(json.loads(response.text))
    except Exception as exc:
        raise RuntimeError(f"Could not parse Gemini outline: {exc}") from exc

    if len(outline.panels) != settings.comic_panels:
        raise RuntimeError(
            f"Gemini returned {len(outline.panels)} panels; expected {settings.comic_panels}."
        )

    return outline
