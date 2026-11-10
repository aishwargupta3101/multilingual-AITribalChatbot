"""Lightweight frontend client for backend-hosted Santali translation models."""
from __future__ import annotations
from typing import Any
import os
import requests
try:
    from api.endpoints import BASE_URL
except ModuleNotFoundError:
    try:
        from frontend.api.endpoints import BASE_URL
    except ModuleNotFoundError:
        # Fallback is only for isolated tests or simple local layouts; normal app uses api.endpoints.
        BASE_URL = os.getenv("TRIBAL_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

SANTALI_TRANSLATE_ENDPOINT = "/api/v1/tribal-languages/santali/translate"


def _translate(text: str, direction: str) -> str:
    clean = str(text or "").strip()
    if not clean:
        raise ValueError("Translation input is empty.")
    if len(clean) > 3000:
        raise ValueError("Text is too long (limit 3,000 characters).")
    try:
        response = requests.post(
            f"{BASE_URL}{SANTALI_TRANSLATE_ENDPOINT}",
            json={"text": clean, "direction": direction},
            timeout=(10, 300),
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach the Santali translation service: {exc}") from exc
    try:
        payload: Any = response.json()
    except ValueError:
        payload = None
    if not response.ok:
        detail = payload.get("detail") or payload.get("error") if isinstance(payload, dict) else None
        detail = detail or response.text[:800] or f"HTTP {response.status_code}"
        raise RuntimeError(f"Santali translation service returned HTTP {response.status_code}: {detail}")
    if not isinstance(payload, dict) or not str(payload.get("translation") or "").strip():
        raise RuntimeError("Santali translation service returned an invalid or empty response.")
    return str(payload["translation"]).strip()


def translate_santali_to_english(text: str) -> str:
    return _translate(text, "santali_to_english")


def translate_english_to_santali(text: str) -> str:
    return _translate(text, "english_to_santali")
