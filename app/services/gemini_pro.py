from __future__ import annotations

import json
import os
from typing import Any

from app.schemas import PanelOutline, PanelStory, PromptRequest

MODEL_NAME = os.getenv("GEMINI_PRO_MODEL", "models/gemini-1.5-pro")


def _fallback_story(outlines: list[PanelOutline], request: PromptRequest) -> list[PanelStory]:
    hero = request.character_name
    voice = {
        "Funny": "with a grin that could power a small rocket",
        "Mysterious": "as the shadows seem to listen back",
        "Hopeful": "with a steady heart and a pocket full of wonder",
        "Dramatic": "while the world holds its breath",
    }.get(request.tone, "with a spark of impossible courage")
    lines = [
        (f"The first clue waits for {hero}, hidden in plain sight. Even {request.setting} feels different {voice}.", f"{hero}: \"Okay, universe. Show me the next page.\""),
        (f"One step becomes three, then a leap. The trail pulls {hero} beyond the safe edge of the familiar.", f"{hero}: \"I can be curious and careful at the same time.\""),
        (f"The challenge arrives louder than expected. For one heartbeat, {hero} considers turning back—but the story is not finished.", f"{hero}: \"Not today. This is where the brave part starts.\""),
        (f"A tiny detail unlocks a much bigger answer. {hero} stops fighting the moment and starts listening to it.", f"{hero}: \"The way through was hiding in the question.\""),
        (f"By the final beat, {hero} has not conquered the world. Better: {hero} has learned how to meet it with open eyes.", f"{hero}: \"Next adventure? I know just where to begin.\""),
    ]
    return [PanelStory(panel_number=i, narration=narration, dialogue=dialogue) for i, (narration, dialogue) in enumerate(lines, 1)]


def _parse_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def _provider_story(outlines: list[PanelOutline], request: PromptRequest) -> list[PanelStory] | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        outline_json = json.dumps([panel.model_dump() for panel in outlines])
        instruction = f"""Expand this five-panel comic outline into concise narration and character dialogue.
Character: {request.character_name}
Tone: {request.tone}
Outline: {outline_json}
Return ONLY a JSON array with exactly five objects. Each object must have panel_number, narration, and dialogue. Keep dialogue short enough for a speech balloon, preserve visual continuity, and write in a cinematic comic voice."""
        response = model.generate_content(instruction, generation_config={"response_mime_type": "application/json", "temperature": 0.9})
        data = _parse_json(response.text)
        if isinstance(data, dict):
            data = data.get("panels", [])
        return [PanelStory.model_validate(item) for item in data][:5]
    except Exception:
        return None


def generate_story_with_mode(outlines: list[PanelOutline], request: PromptRequest) -> tuple[list[PanelStory], bool]:
    """Return the story layer and whether the local fallback was used."""
    stories = _provider_story(outlines, request)
    if stories and len(stories) == 5:
        return stories, False
    return _fallback_story(outlines, request), True


def generate_story(outlines: list[PanelOutline], request: PromptRequest) -> list[PanelStory]:
    """Use Gemini Pro when configured, otherwise return a deterministic story layer."""
    return generate_story_with_mode(outlines, request)[0]
