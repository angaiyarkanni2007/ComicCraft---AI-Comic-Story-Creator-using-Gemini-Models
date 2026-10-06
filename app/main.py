from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import router
from app.schemas import HealthResponse

ROOT_DIR = Path(__file__).resolve().parents[1]
app = FastAPI(title="ComicCraft — AI Comic Story Creator", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "app" / "static")), name="static")
app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="comiccraft", mode="gemini-and-stable-diffusion-ready")


@app.get("/manus-routes.json")
def route_manifest():
    manifest = ROOT_DIR / "route-manifest.json"
    return FileResponse(manifest, media_type="application/json", headers={"Cache-Control": "no-cache"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "3000")), reload=True)
