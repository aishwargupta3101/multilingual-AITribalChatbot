"""Frontend helper: English/Hindi <-> Gondi via existing Hindi MT + local Gondi MT5.

The local Gondi model only supports Hindi <-> Gondi. English requests are bridged
through the project's existing English/Hindi translation endpoint.
"""
from __future__ import annotations

import requests
try:
    from api.endpoints import BASE_URL
except ModuleNotFoundError:
    from frontend.api.endpoints import BASE_URL

TIMEOUT = 300


def _existing_translation(text: str, source_language: str, target_language: str) -> str:
    response = requests.post(
        f"{BASE_URL}/api/v1/translation/translate",
        json={"text": text, "source_language": source_language, "target_language": target_language},
        timeout=TIMEOUT,
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    if not response.ok:
        detail = payload.get("detail") or payload.get("error") or response.text[:400]
        raise RuntimeError(f"Existing {source_language}-to-{target_language} translation failed: {detail}")
    translated = payload.get("translated_text") or payload.get("translation") or payload.get("text") or ""
    if not isinstance(translated, str) or not translated.strip():
        raise RuntimeError(f"Existing translation service returned no {target_language} text.")
    return translated.strip()


def _local_hindi_gondi(text: str, direction: str) -> str:
    response = requests.post(
        f"{BASE_URL}/api/v1/tribal-languages/gondi/translate",
        json={"text": text, "direction": direction},
        timeout=TIMEOUT,
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    if not response.ok:
        detail = payload.get("detail") or payload.get("error") or response.text[:400]
        raise RuntimeError(f"Local Gondi translation is unavailable: {detail}")
    translated = payload.get("translation")
    if not isinstance(translated, str) or not translated.strip():
        raise RuntimeError("Local Gondi translation model returned no translated text.")
    return translated.strip()


def translate_gondi(text: str, direction: str) -> str:
    """Translate English/Gondi or Hindi/Gondi text with explicit stage checks."""
    value = str(text or "").strip()
    if not value:
        raise ValueError("Gondi translation input is empty.")
    normalized = str(direction or "").strip().lower().replace("-", "_")
    if normalized == "hindi_to_gondi":
        return _local_hindi_gondi(value, "hindi_to_gondi")
    if normalized == "gondi_to_hindi":
        return _local_hindi_gondi(value, "gondi_to_hindi")
    if normalized == "english_to_gondi":
        hindi = _existing_translation(value, "english", "hindi")
        return _local_hindi_gondi(hindi, "hindi_to_gondi")
    if normalized == "gondi_to_english":
        hindi = _local_hindi_gondi(value, "gondi_to_hindi")
        return _existing_translation(hindi, "hindi", "english")
    raise ValueError("Supported Gondi directions: English↔Gondi and Hindi↔Gondi.")
