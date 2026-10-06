from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=8, max_length=800)
    character_name: str = Field(default="Nova", min_length=1, max_length=40)
    setting: str = Field(default="an enchanted forest", min_length=2, max_length=120)
    tone: str = Field(default="Dramatic", min_length=2, max_length=40)
    art_style: str = Field(default="Comic book", min_length=2, max_length=60)

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class PanelOutline(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1, max_length=120)
    scene_description: str = Field(..., min_length=1, max_length=600)
    image_prompt: str = Field(..., min_length=1, max_length=900)


class PanelStory(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)
    narration: str = Field(..., min_length=1, max_length=600)
    dialogue: str = Field(..., min_length=1, max_length=300)


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    narration: str
    dialogue: str
    image_url: str
    image_path: str


class GenerationMeta(BaseModel):
    outline_model: str
    story_model: str
    image_model: str
    fallback_mode: bool = True


class ComicLayout(BaseModel):
    title: str
    prompt: PromptRequest
    panels: list[ComicPanel]
    pdf_url: str
    meta: GenerationMeta


class ComicResponse(BaseModel):
    success: bool = True
    comic: ComicLayout


class ImageTestRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=900)
    art_style: str = Field(default="Comic book", min_length=2, max_length=60)


class ImageTestResponse(BaseModel):
    success: bool = True
    image_url: str
    model: str


class HealthResponse(BaseModel):
    status: str
    service: str
    mode: str
