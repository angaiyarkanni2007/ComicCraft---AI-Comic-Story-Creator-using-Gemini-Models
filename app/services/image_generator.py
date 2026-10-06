from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parents[2]
PANEL_DIR = ROOT_DIR / "app" / "static" / "panels"
DIFFUSERS_MODEL = os.getenv("DIFFUSERS_MODEL_ID", "runwayml/stable-diffusion-v1-5")


def _safe_stem(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return cleaned[:48] or "panel"


def _font(size: int) -> ImageFont.ImageFont:
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _fallback_image(prompt: str, panel_number: int, art_style: str, path: Path) -> None:
    digest = hashlib.sha256(prompt.encode("utf-8")).digest()
    bg = (248, 241, 231)
    ink = (23, 21, 31)
    violet = (118, 87, 255)
    coral = (255, 111, 97)
    yellow = (255, 200, 87)
    accent = (80 + digest[0] // 3, 90 + digest[1] // 4, 130 + digest[2] // 3)
    image = Image.new("RGB", (1200, 800), bg)
    draw = ImageDraw.Draw(image)
    # Ink frame and halftone sky.
    draw.rectangle((22, 22, 1178, 778), outline=ink, width=18)
    for x in range(520, 1120, 26):
        for y in range(80, 360, 26):
            if ((x + y + digest[3]) // 26) % 3 == 0:
                draw.ellipse((x, y, x + 7, y + 7), fill=(220, 211, 200))
    # Environment blocks vary by prompt hash.
    horizon = 490 + digest[4] % 70
    draw.rectangle((40, horizon, 1160, 760), fill=accent)
    for index in range(7):
        x = 80 + index * 150 + digest[5] % 25
        height = 100 + (digest[(index + 6) % len(digest)] % 150)
        draw.polygon([(x, horizon), (x + 70, horizon - height), (x + 140, horizon)], fill=(44, 55, 68))
    # Sun/comet and central hero silhouette.
    sun_x = 950 - digest[7] % 100
    draw.ellipse((sun_x - 70, 100, sun_x + 70, 240), fill=yellow, outline=ink, width=8)
    hero_x = 560 + (digest[8] % 100) - 50
    draw.ellipse((hero_x, 270, hero_x + 120, 390), fill=coral, outline=ink, width=10)
    draw.polygon([(hero_x - 35, 390), (hero_x + 155, 390), (hero_x + 185, 610), (hero_x - 65, 610)], fill=violet, outline=ink)
    draw.line((hero_x + 10, 500, hero_x - 120, 610), fill=ink, width=18)
    draw.line((hero_x + 125, 500, hero_x + 245, 560), fill=ink, width=18)
    draw.ellipse((hero_x + 38, 315, hero_x + 58, 340), fill=ink)
    draw.ellipse((hero_x + 82, 315, hero_x + 102, 340), fill=ink)
    # Speech bubble is intentionally text-free; narration lives in the UI/PDF.
    bubble = (110, 100, 430, 235)
    draw.rounded_rectangle(bubble, radius=28, fill="white", outline=ink, width=8)
    draw.polygon([(250, 235), (290, 290), (320, 235)], fill="white", outline=ink)
    draw.ellipse((170, 150, 195, 175), fill=coral)
    draw.ellipse((225, 150, 250, 175), fill=violet)
    draw.ellipse((280, 150, 305, 175), fill=yellow)
    draw.text((55, 40), f"PANEL {panel_number:02d}", font=_font(28), fill=ink)
    label = "LOCAL COMIC RENDERER" if "Comic" in art_style else art_style.upper()
    draw.text((55, 720), label[:24], font=_font(23), fill=ink)
    image.save(path, format="PNG", optimize=True)


def _diffusers_image(prompt: str, path: Path) -> bool:
    if os.getenv("DIFFUSERS_ENABLED", "0").lower() not in {"1", "true", "yes"}:
        return False
    try:
        import torch
        from diffusers import StableDiffusionPipeline

        pipe = StableDiffusionPipeline.from_pretrained(DIFFUSERS_MODEL, torch_dtype=torch.float32)
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        image = pipe(prompt, num_inference_steps=20, guidance_scale=7.0).images[0]
        image.save(path, format="PNG")
        return True
    except Exception:
        return False


def generate_image_with_mode(prompt: str, panel_number: int, art_style: str) -> tuple[Path, bool]:
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{panel_number:02d}-{_safe_stem(prompt)}.png"
    path = PANEL_DIR / filename
    used_provider = _diffusers_image(prompt, path)
    if not used_provider:
        _fallback_image(prompt, panel_number, art_style, path)
    return path, used_provider


def generate_image(prompt: str, panel_number: int, art_style: str) -> Path:
    return generate_image_with_mode(prompt, panel_number, art_style)[0]


def image_model_label(used_provider: bool | None = None) -> str:
    enabled = os.getenv("DIFFUSERS_ENABLED", "0").lower() in {"1", "true", "yes"}
    if enabled and used_provider is False:
        return "Stable Diffusion requested · local fallback"
    if enabled and used_provider is True:
        return f"Stable Diffusion · {DIFFUSERS_MODEL}"
    return f"Stable Diffusion · {DIFFUSERS_MODEL}" if enabled else "Local comic renderer · SD-ready"
