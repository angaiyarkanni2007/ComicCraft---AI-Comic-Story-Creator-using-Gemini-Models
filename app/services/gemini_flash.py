from __future__ import annotations

import json
import os
from typing import Any

from app.schemas import PanelOutline, PromptRequest

MODEL_NAME = os.getenv("GEMINI_FLASH_MODEL", "models/gemini-1.5-flash")


def _fallback_outline(request: PromptRequest) -> list[PanelOutline]:
    hero = request.character_name
    setting = request.setting
    prompt = request.story_prompt
    beats = [
        ("The spark", f"{hero} discovers the first impossible clue inside {setting}, while the idea from the story comes into focus.", "wide establishing shot, curious hero, first magical clue, layered environment"),
        ("Into the unknown", f"{hero} follows the clue deeper into {setting}; the world shifts around the hero and the stakes become clear.", "dynamic tracking shot, hero moving through the setting, swirling motion lines, expressive face"),
        ("The turning point", f"A sudden obstacle challenges {hero}. The central problem from \"{prompt}\" becomes personal and urgent.", "dramatic low angle, obstacle filling the foreground, bold ink shadows, comic action composition"),
        ("A clever answer", f"{hero} notices an unexpected detail and turns the obstacle into a chance to act with courage.", "heroic close-up, clever discovery, bright accent light, crisp comic panel framing"),
        ("A new page", f"The adventure resolves with a memorable image: {hero} carries the lesson forward, changed but ready for the next story.", "hopeful final wide shot, hero silhouetted against a warm sky, celebratory comic-book energy"),
    ]
    return [
        PanelOutline(
            panel_number=index,
            title=title,
            scene_description=description,
            image_prompt=f"{style_hint}, {request.art_style} illustration, {request.tone} tone, coherent character design for {hero}, no text in image",
        )
        for index, (title, description, style_hint) in enumerate(beats, start=1)
    ]


def _parse_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def _provider_outline(request: PromptRequest) -> list[PanelOutline] | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        instruction = f"""Create exactly five comic panels for this brief.
Story prompt: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}
Return ONLY a JSON array. Each item must have panel_number, title, scene_description, and image_prompt. Keep visual continuity and never place text inside the image prompt."""
        response = model.generate_content(
            instruction,
            generation_config={"response_mime_type": "application/json", "temperature": 0.85},
        )
        data = _parse_json(response.text)
        if isinstance(data, dict):
            data = data.get("panels", [])
        return [PanelOutline.model_validate(item) for item in data][:5]
    except Exception:
        return None


def generate_outline_with_mode(request: PromptRequest) -> tuple[list[PanelOutline], bool]:
    """Return the outline and whether the local fallback was used."""
    panels = _provider_outline(request)
    if panels and len(panels) == 5:
        return panels, False
    return _fallback_outline(request), True


def generate_outline(request: PromptRequest) -> list[PanelOutline]:
    """Use Gemini Flash when configured, otherwise return a polished local outline."""
    return generate_outline_with_mode(request)[0]
