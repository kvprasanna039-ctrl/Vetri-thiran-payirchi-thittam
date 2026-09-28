from pydantic import BaseModel, Field, field_validator


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=120)
    scene_description: str = Field(min_length=1, max_length=800)
    image_prompt: str = Field(min_length=1, max_length=1500)


class ComicOutline(BaseModel):
    panels: list[PanelOutline] = Field(min_length=1, max_length=10)


class PanelStory(BaseModel):
    panel_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=120)
    scene_description: str = Field(min_length=1, max_length=800)
    caption: str = Field(default="", max_length=500)
    narration: str = Field(default="", max_length=1500)
    dialogue: str = Field(default="", max_length=1500)
    image_prompt: str = Field(min_length=1, max_length=1500)


class ComicStory(BaseModel):
    panels: list[PanelStory] = Field(min_length=1, max_length=10)


class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=3, max_length=1200)
    character_name: str = Field(min_length=1, max_length=80)
    setting: str = Field(min_length=1, max_length=120)
    tone: str = Field(min_length=1, max_length=80)
    art_style: str = Field(min_length=1, max_length=120)

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty.")
        return value


class ImageTestRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1500)
