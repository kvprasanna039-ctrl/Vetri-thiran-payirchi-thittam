from pathlib import Path
from typing import Iterable

from app.models import ComicStory


def build_comic_layout(story: ComicStory, image_paths: Iterable[str]) -> list[dict]:
    images = list(image_paths)
    if len(images) != len(story.panels):
        raise ValueError("Number of images must match number of story panels.")

    layout = []
    for panel, image_path in zip(story.panels, images):
        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "image_path": image_path,
                "image_url": "/" + str(Path(image_path).as_posix()).lstrip("/"),
                "scene_description": panel.scene_description,
                "caption": panel.caption,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
                "image_prompt": panel.image_prompt,
            }
        )
    return layout
