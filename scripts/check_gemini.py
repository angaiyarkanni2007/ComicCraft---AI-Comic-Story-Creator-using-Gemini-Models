#!/usr/bin/env python3
"""Check Gemini credentials and model connectivity before starting Uvicorn."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any


DEFAULT_MODEL = "models/gemini-1.5-flash"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a minimal request to Gemini and verify the configured API key."
    )
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_FLASH_MODEL", DEFAULT_MODEL),
        help=f"Gemini model ID (default: $GEMINI_FLASH_MODEL or {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--prompt",
        default="Reply with exactly GEMINI_OK and nothing else.",
        help="Small test prompt to send to Gemini.",
    )
    return parser.parse_args()


def load_dotenv_file() -> None:
    """Load simple KEY=value entries without adding a dotenv dependency."""
    dotenv_path = os.getenv("DOTENV_PATH", ".env")
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, encoding="utf-8") as dotenv:
        for raw_line in dotenv:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def response_text(response: Any) -> str:
    try:
        text = response.text
    except Exception:
        text = ""
    return " ".join(str(text or "").split())


def main() -> int:
    load_dotenv_file()
    args = parse_args()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        print("FAIL: GEMINI_API_KEY is not set.", file=sys.stderr)
        print("Set it in the environment or in .env before starting Uvicorn.", file=sys.stderr)
        return 2

    try:
        import google.generativeai as genai
    except ImportError:
        print("FAIL: google-generativeai is not installed.", file=sys.stderr)
        print("Run: python3 -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    print(f"Checking Gemini model: {args.model}")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(args.model)
        response = model.generate_content(
            args.prompt,
            generation_config={"temperature": 0, "max_output_tokens": 16},
        )
        text = response_text(response)
        if not text:
            print("FAIL: Gemini returned an empty response.", file=sys.stderr)
            return 1
        print("PASS: Gemini API key is valid and the model responded.")
        print(f"Response: {text[:160]}")
        return 0
    except Exception as exc:
        error = " ".join(str(exc).split())
        print("FAIL: Gemini request did not succeed.", file=sys.stderr)
        print(f"Reason: {error[:500]}", file=sys.stderr)
        print("Tip: verify the key, model ID, network access, and API quota.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
