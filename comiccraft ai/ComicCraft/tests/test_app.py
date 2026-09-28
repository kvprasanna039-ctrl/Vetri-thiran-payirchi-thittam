from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.models import ComicStory, PanelStory
from app.services.exporters import save_pdf
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "Create My Comic" in response.text


def test_validation():
    response = client.post(
        "/generate-comic/json",
        json={
            "story_prompt": "x",
            "character_name": "",
            "setting": "forest",
            "tone": "funny",
            "art_style": "anime",
        },
    )
    assert response.status_code == 422


def test_placeholder_image():
    path = generate_image("A fox in an enchanted forest", 1)
    assert Path(path).exists()


def test_layout_and_pdf():
    story = ComicStory(
        panels=[
            PanelStory(
                panel_number=1,
                title="Beginning",
                scene_description="A hero enters a forest.",
                caption="The journey begins.",
                narration="Kavi steps into the forest.",
                dialogue="Kavi: Hello, forest!",
                image_prompt="A hero in a forest",
            )
        ]
    )
    image_path = generate_image("A hero in a forest", 1)
    layout = build_comic_layout(story, [image_path])
    assert layout[0]["panel_number"] == 1

    pdf = save_pdf(layout, filename_prefix="test")
    assert Path(pdf).exists()
    Path(pdf).unlink()
