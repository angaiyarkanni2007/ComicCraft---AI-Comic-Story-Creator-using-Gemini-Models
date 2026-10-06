from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.schemas import ComicResponse, ImageTestRequest, ImageTestResponse, PromptRequest
from app.services.image_generator import generate_image_with_mode, image_model_label
from app.services.pipeline import create_comic

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate")
def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Nova"),
    setting: str = Form("an enchanted forest"),
    tone: str = Form("Dramatic"),
    art_style: str = Form("Comic book"),
):
    payload = PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )
    try:
        comic = create_comic(payload)
    except Exception:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error_message": "The ink pass stalled. Your brief is safe—try again, or adjust the tone and style.",
                "form_data": payload.model_dump(),
            },
            status_code=500,
        )
    return templates.TemplateResponse(
        "comic_preview.html",
        {"request": request, "comic": comic.comic.model_dump(mode="json")},
    )


@router.post("/generate-comic/json", response_model=ComicResponse)
def generate_json(payload: PromptRequest):
    comic = create_comic(payload)
    return JSONResponse(content=comic.model_dump(mode="json"), headers={"Cache-Control": "private, no-store"})


@router.post("/test-image", response_model=ImageTestResponse)
def test_image(payload: ImageTestRequest):
    path, used_provider = generate_image_with_mode(payload.prompt, 0, payload.art_style)
    return JSONResponse(
        content={"success": True, "image_url": f"/static/panels/{path.name}", "model": image_model_label(used_provider)},
        headers={"Cache-Control": "private, no-store"},
    )


@router.get("/export-success")
def export_success(request: Request):
    return templates.TemplateResponse("export_success.html", {"request": request})
