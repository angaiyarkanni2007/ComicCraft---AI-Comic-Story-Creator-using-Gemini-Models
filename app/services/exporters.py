from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.schemas import ComicPanel, PromptRequest

ROOT_DIR = Path(__file__).resolve().parents[2]
EXPORT_DIR = ROOT_DIR / "app" / "static" / "exports"


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:48] or "comic"


def _pdf_text(value: str) -> str:
    replacements = {"’": "'", "“": '"', "”": '"', "—": "-", "–": "-", "…": "..."}
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("latin-1", "replace").decode("latin-1")


def save_pdf(request: PromptRequest, panels: list[ComicPanel]) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"comiccraft-{_safe_filename(request.character_name)}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
    path = EXPORT_DIR / filename
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    for panel in panels:
        pdf.add_page()
        pdf.set_fill_color(248, 241, 231)
        pdf.rect(0, 0, 210, 297, style="F")
        pdf.set_draw_color(23, 21, 31)
        pdf.set_line_width(1.2)
        pdf.rect(10, 10, 190, 277)
        pdf.set_text_color(23, 21, 31)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 8, _pdf_text(f"COMICCRAFT  /  PANEL {panel.panel_number:02d}"), ln=True)
        pdf.set_font("Helvetica", "B", 19)
        pdf.multi_cell(0, 10, _pdf_text(panel.title))
        image_path = Path(panel.image_path)
        if image_path.exists():
            pdf.image(str(image_path), x=19, y=44, w=172, h=114)
        pdf.set_y(166)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, _pdf_text("SCENE"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _pdf_text(panel.scene_description))
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, _pdf_text("NARRATION"), ln=True)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, _pdf_text(panel.narration))
        pdf.ln(3)
        pdf.set_fill_color(118, 87, 255)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 9, _pdf_text(panel.dialogue), fill=True)
        pdf.set_text_color(23, 21, 31)
    pdf.output(str(path))
    return path
