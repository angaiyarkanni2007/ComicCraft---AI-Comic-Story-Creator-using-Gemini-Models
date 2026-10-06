from __future__ import annotations

from pathlib import Path

from app.schemas import ComicPanel, PanelOutline, PanelStory, PromptRequest


def build_comic_layout(
    request: PromptRequest,
    outlines: list[PanelOutline],
    stories: list[PanelStory],
    image_paths: list[Path],
) -> list[ComicPanel]:
    story_by_panel = {story.panel_number: story for story in stories}
    image_by_panel = {index + 1: path for index, path in enumerate(image_paths)}
    panels: list[ComicPanel] = []
    for outline in outlines:
        story = story_by_panel[outline.panel_number]
        image_path = image_by_panel[outline.panel_number]
        panels.append(
            ComicPanel(
                panel_number=outline.panel_number,
                title=outline.title,
                scene_description=outline.scene_description,
                image_prompt=outline.image_prompt,
                narration=story.narration,
                dialogue=story.dialogue,
                image_url=f"/static/panels/{image_path.name}",
                image_path=str(image_path),
            )
        )
    return panels
