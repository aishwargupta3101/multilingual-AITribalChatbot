"""Lightweight frontend client for backend-hosted Santali text-to-speech."""
from __future__ import annotations
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

SANTALI_TTS_ENDPOINT = "/api/v1/tribal-languages/santali/tts"


def synthesize_santali_wav(text: str) -> bytes:
    clean = str(text or "").strip()
    if not clean:
        raise ValueError("Santali TTS input is empty.")
    if len(clean) > 1200:
        raise ValueError("Santali TTS input is too long (limit 1,200 characters).")
    try:
        response = requests.post(
            f"{BASE_URL}{SANTALI_TTS_ENDPOINT}",
            json={"text": clean},
            timeout=(10, 300),
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach the Santali speech service: {exc}") from exc
    if not response.ok:
        try:
            payload = response.json()
        except ValueError:
            payload = None
        detail = payload.get("detail") or payload.get("error") if isinstance(payload, dict) else None
        detail = detail or response.text[:800] or f"HTTP {response.status_code}"
        raise RuntimeError(f"Santali speech service returned HTTP {response.status_code}: {detail}")
    content_type = response.headers.get("content-type", "").lower()
    if not response.content or (content_type and "audio/" not in content_type and "octet-stream" not in content_type):
        raise RuntimeError("Santali speech service returned an empty or non-audio response.")
    return response.content
