# ComicCraft — AI Comic Story Creator

ComicCraft turns a short story brief into a five-panel comic with a structured outline, narration, dialogue, illustrations, and a downloadable PDF. It is implemented as a FastAPI/Jinja2 application with optional Gemini Flash, Gemini Pro, and Stable Diffusion integrations.

## Run locally

```bash
python3 -m pip install -r requirements.txt
PORT=3000 uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

Open `http://127.0.0.1:3000`. The API schema is available at `/docs` and readiness is available at `/health`.

## Check Gemini before starting Uvicorn

Run the preflight script from the project root:

```bash
python3 scripts/check_gemini.py
```

It loads `GEMINI_API_KEY` from the environment or a local `.env`, calls the configured Flash model, prints a redacted pass/fail result, and exits with `0` on success, `1` when Gemini rejects the request, or `2` when local configuration/dependencies are missing. Override the model or prompt when needed:

```bash
python3 scripts/check_gemini.py --model gemini-2.5-flash
python3 scripts/check_gemini.py --prompt "Reply with READY"
```

## Model configuration

The app is intentionally usable without credentials or a model download. By default it uses a deterministic local outline/story fallback and a lightweight PIL comic renderer so the whole product can be previewed quickly.

To enable Gemini, set `GEMINI_API_KEY`. Optional model overrides are `GEMINI_FLASH_MODEL` (default `models/gemini-1.5-flash`) and `GEMINI_PRO_MODEL` (default `models/gemini-1.5-pro`). To opt into lazy Diffusers generation, first install `python3 -m pip install -r requirements-ml.txt`, then set `DIFFUSERS_ENABLED=1` and optionally `DIFFUSERS_MODEL_ID` (default `runwayml/stable-diffusion-v1-5`). Diffusers is intentionally not loaded during startup and the base install does not pull heavyweight ML wheels. The preview ribbon reports whether a provider pass or local fallback produced the issue.

## Routes

- `GET /` — story brief form
- `POST /generate` — HTML form generation and preview
- `POST /generate-comic/json` — typed JSON generation endpoint
- `POST /test-image` — standalone image test endpoint
- `GET /export-success` — export confirmation page
- `GET /health` — managed health check
- `GET /manus-routes.json` — current page route manifest

Generated panels are written to `app/static/panels`, and PDFs are written to `app/static/exports`. These are workspace artifacts in the first version; durable storage can be added later.


## Fresh Windows setup

This copy is prepared for **Python 3.12**, which has compatible Windows wheels for the pinned Pillow dependency. Do not use Python 3.14 for this version.

In PowerShell from the project folder:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_windows.ps1
notepad .env
.\.venv\Scripts\python.exe scripts\check_gemini.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 3000 --reload --env-file .env
```

Open `http://127.0.0.1:3000`. If Python 3.12 is not installed, install Python 3.12 64-bit from [python.org](https://www.python.org/downloads/) with the Python Launcher enabled, then rerun the setup script.
