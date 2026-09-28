from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


def _safe_name(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")
    return text[:60] or "panel"


def _placeholder(prompt: str, output: Path, panel_number: int) -> str:
    settings = get_settings()
    image = Image.new("RGB", (settings.image_width, settings.image_height), "#f4ead5")
    draw = ImageDraw.Draw(image)

    try:
        font_large = ImageFont.truetype("arial.ttf", 34)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.rectangle(
        (18, 18, settings.image_width - 18, settings.image_height - 18),
        outline="#1e1e1e",
        width=5,
    )
    draw.text((35, 35), f"COMIC PANEL {panel_number}", fill="#1e1e1e", font=font_large)

    words = prompt.replace("\n", " ").split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > 42:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)

    y = 125
    for line in lines[:12]:
        draw.text((35, y), line, fill="#333333", font=font_small)
        y += 27

    draw.ellipse(
        (settings.image_width - 180, settings.image_height - 180,
         settings.image_width - 55, settings.image_height - 55),
        outline="#1e1e1e",
        width=5,
    )
    draw.text(
        (settings.image_width - 155, settings.image_height - 135),
        "AI",
        fill="#1e1e1e",
        font=font_large,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG")
    return str(output)


@lru_cache(maxsize=1)
def _load_diffusers_pipeline():
    import torch
    from diffusers import StableDiffusionPipeline

    settings = get_settings()
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = StableDiffusionPipeline.from_pretrained(
        settings.diffusion_model,
        torch_dtype=dtype,
        use_safetensors=True,
    )

    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        pipe.enable_attention_slicing()
    else:
        pipe = pipe.to("cpu")

    return pipe


def _generate_diffusers(prompt: str, output: Path) -> str:
    settings = get_settings()
    pipe = _load_diffusers_pipeline()
    result = pipe(
        prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    )
    result.images[0].save(output, "PNG")
    return str(output)


def _generate_huggingface(prompt: str, output: Path) -> str:
    settings = get_settings()
    if not settings.hf_api_key:
        raise RuntimeError("HF_API_KEY is required for IMAGE_PROVIDER=huggingface.")

    from huggingface_hub import InferenceClient

    client = InferenceClient(provider="hf-inference", api_key=settings.hf_api_key)
    image = client.text_to_image(prompt, model=settings.diffusion_model)
    image.save(output, "PNG")
    return str(output)


def generate_image(prompt: str, panel_number: int) -> str:
    settings = get_settings()
    filename = f"panel_{panel_number}_{uuid4().hex[:8]}_{_safe_name(prompt)}.png"
    output = settings.panels_dir / filename
    provider = settings.image_provider.lower().strip()

    if provider == "placeholder":
        return _placeholder(prompt, output, panel_number)
    if provider == "diffusers":
        return _generate_diffusers(prompt, output)
    if provider == "huggingface":
        return _generate_huggingface(prompt, output)

    raise RuntimeError(
        "IMAGE_PROVIDER must be placeholder, diffusers, or huggingface."
    )
