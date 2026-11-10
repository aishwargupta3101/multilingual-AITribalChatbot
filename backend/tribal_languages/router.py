"""FastAPI router for the experimental Tribal Language Lab.

This router exposes capability metadata only. It does not invoke speech,
translation, or TTS inference until verified backends are explicitly connected.
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/tribal-languages", tags=["Tribal Language Lab"])

EXPERIMENTAL_LANGUAGES = {
    "gondi": {
        "display_name": "Gondi",
        "stt": {"status": "experimental", "enabled": False},
        "translation": {"status": "experimental", "enabled": False},
        "tts": {"status": "experimental", "enabled": False},
        "notes": "Verify the specific Gondi variety, model compatibility, and licence.",
    },
    "santali": {
        "display_name": "Santali",
        "stt": {"status": "experimental", "enabled": False},
        "translation": {"status": "experimental", "enabled": False},
        "tts": {"status": "experimental", "enabled": False},
        "notes": "Verify dataset availability, writing system, model compatibility, and licence.",
    },
    "monpa": {
        "display_name": "Monpa",
        "stt": {"status": "experimental", "enabled": False},
        "translation": {"status": "experimental", "enabled": False},
        "tts": {"status": "experimental", "enabled": False},
        "notes": "Select and verify a specific Monpa variety before enabling models.",
    },
}


@router.get("/health")
async def tribal_language_lab_health():
    """Return status of the experimental language lab."""
    return {
        "service": "tribal-language-lab",
        "status": "running",
        "mode": "metadata-only",
        "inference_enabled": False,
    }


@router.get("/languages")
async def list_experimental_languages():
    """List experimental languages and current capability readiness."""
    return {
        "languages": [
            {"code": code, **details}
            for code, details in EXPERIMENTAL_LANGUAGES.items()
        ]
    }


@router.get("/languages/{language_code}")
async def get_experimental_language(language_code: str):
    """Return readiness details for one experimental language."""
    code = language_code.strip().lower()
    details = EXPERIMENTAL_LANGUAGES.get(code)
    if details is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Unknown experimental language: {code}")
    return {"code": code, **details}
