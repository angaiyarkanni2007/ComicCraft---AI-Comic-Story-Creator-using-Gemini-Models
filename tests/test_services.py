from pathlib import Path

from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


def test_fallback_pipeline_shapes_five_panels():
    request = PromptRequest(story_prompt="A fox finds a door in an old tree.", character_name="Moxie")
    outlines = generate_outline(request)
    stories = generate_story(outlines, request)
    images = [generate_image(panel.image_prompt, panel.panel_number, request.art_style) for panel in outlines]
    layout = build_comic_layout(request, outlines, stories, images)

    assert len(outlines) == 5
    assert len(stories) == 5
    assert len(layout) == 5
    assert all(panel.image_url.startswith("/static/panels/") for panel in layout)
    assert all(Path(panel.image_path).exists() for panel in layout)


def test_pdf_export_creates_timestamped_file(tmp_path, monkeypatch):
    request = PromptRequest(story_prompt="A fox finds a door in an old tree.", character_name="Moxie")
    outlines = generate_outline(request)
    stories = generate_story(outlines, request)
    images = [generate_image(panel.image_prompt, panel.panel_number, request.art_style) for panel in outlines]
    layout = build_comic_layout(request, outlines, stories, images)

    import app.services.exporters as exporters
    monkeypatch.setattr(exporters, "EXPORT_DIR", tmp_path)
    output = save_pdf(request, layout)

    assert output.exists()
    assert output.suffix == ".pdf"
    assert output.stat().st_size > 1000
