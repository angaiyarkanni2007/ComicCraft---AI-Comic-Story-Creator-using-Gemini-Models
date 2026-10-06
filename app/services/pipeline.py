from __future__ import annotations

from app.schemas import ComicLayout, ComicResponse, GenerationMeta, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import MODEL_NAME as FLASH_MODEL, generate_outline_with_mode
from app.services.gemini_pro import MODEL_NAME as PRO_MODEL, generate_story_with_mode
from app.services.image_generator import generate_image_with_mode, image_model_label
from app.services.layout_builder import build_comic_layout


def create_comic(request: PromptRequest) -> ComicResponse:
    outlines, outline_fallback = generate_outline_with_mode(request)
    stories, story_fallback = generate_story_with_mode(outlines, request)
    generated = [generate_image_with_mode(panel.image_prompt, panel.panel_number, request.art_style) for panel in outlines]
    image_paths = [path for path, _ in generated]
    image_provider_success = all(used_provider for _, used_provider in generated)
    panels = build_comic_layout(request, outlines, stories, image_paths)
    pdf_path = save_pdf(request, panels)
    meta = GenerationMeta(
        outline_model=FLASH_MODEL,
        story_model=PRO_MODEL,
        image_model=image_model_label(image_provider_success),
        fallback_mode=outline_fallback or story_fallback or not image_provider_success,
    )
    layout = ComicLayout(
        title=f"{request.character_name}'s next chapter",
        prompt=request,
        panels=panels,
        pdf_url=f"/static/exports/{pdf_path.name}",
        meta=meta,
    )
    return ComicResponse(comic=layout)
