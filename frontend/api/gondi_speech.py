"""Frontend HTTP helpers for Gondi MMS speech endpoints."""
from __future__ import annotations

import requests
try:
    from api.endpoints import BASE_URL
except ModuleNotFoundError:
    from frontend.api.endpoints import BASE_URL


def transcribe_gondi_audio(audio_bytes: bytes, filename: str = "gondi.wav") -> dict:
    response = requests.post(
        f"{BASE_URL}/api/v1/tribal-languages/gondi/asr",
        files={"audio": (filename, audio_bytes, "audio/wav")},
        timeout=600,
    )
    try:
        data = response.json()
    except ValueError:
        data = {}
    if not response.ok:
        detail = data.get("detail") or response.text[:500] or "Unknown Gondi ASR error"
        raise RuntimeError(str(detail))
    if not isinstance(data, dict) or not data.get("success"):
        raise RuntimeError("Gondi ASR returned an invalid response.")
    return data


def synthesize_gondi_audio(text: str) -> bytes:
    response = requests.post(
        f"{BASE_URL}/api/v1/tribal-languages/gondi/tts",
        json={"text": str(text or "")},
        timeout=600,
    )
    if not response.ok:
        try:
            data = response.json()
        except ValueError:
            data = {}
        detail = data.get("detail") or response.text[:500] or "Unknown Gondi TTS error"
        raise RuntimeError(str(detail))
    if not response.content:
        raise RuntimeError("Gondi TTS returned empty audio.")
    return response.content
