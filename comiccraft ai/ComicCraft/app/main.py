from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI comic story creator using Gemini and image generation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "image_provider": settings.image_provider,
        "gemini_configured": bool(settings.gemini_api_key),
    }
