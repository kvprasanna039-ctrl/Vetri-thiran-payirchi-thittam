# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that turns a user's story idea into a five-panel comic.

Pipeline:
1. Gemini Flash -> structured panel outline.
2. Gemini Pro -> narration and dialogue.
3. Stable Diffusion/Diffusers -> panel illustrations.
4. Layout builder -> combines images and story data.
5. FPDF2 -> downloadable PDF.

The supplied project document uses older Gemini 1.5 model names. This implementation uses the current Google GenAI Python SDK and configurable model IDs, while preserving the documented Flash/Pro roles.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   └── services/
│       ├── __init__.py
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       ├── layout_builder.py
│       └── exporters.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── panels/.gitkeep
│   └── exports/.gitkeep
├── tests/test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Windows / VS Code setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add:

```env
GEMINI_API_KEY=your_key_here
```

Start:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` and API docs at `http://127.0.0.1:8000/docs`.

## Image providers

For the first smoke test, keep:

```env
IMAGE_PROVIDER=placeholder
```

This verifies Gemini + FastAPI + PDF without downloading a diffusion checkpoint.

For local Stable Diffusion:

```env
IMAGE_PROVIDER=diffusers
```

A CUDA GPU is strongly recommended.

For Hugging Face hosted inference:

```env
IMAGE_PROVIDER=huggingface
HF_API_KEY=your_huggingface_token
```

## JSON API

`POST /generate-comic/json`

```json
{
  "story_prompt": "A brave fox explores an enchanted forest and discovers a forgotten moon temple.",
  "character_name": "Kavi",
  "setting": "enchanted forest",
  "tone": "dramatic",
  "art_style": "comic book"
}
```

## Image test API

`POST /test-image`

```json
{
  "prompt": "A brave fox beneath a glowing moon in an enchanted forest, comic book style"
}
```

## Tests

```powershell
pytest -q
```

Tests avoid live Gemini/image-model calls where possible and cover validation, routing, layout, PDF export and placeholder image creation.

## Troubleshooting

- If Gemini fails, check `GEMINI_API_KEY` and the model IDs in `.env`.
- If local Diffusers is too slow or runs out of memory, use `IMAGE_PROVIDER=placeholder` or the Hugging Face provider.
- Generated panel images are stored in `static/panels/`; PDFs are stored in `static/exports/`.
- Never commit `.env`.
