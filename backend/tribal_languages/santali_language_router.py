"""Backend endpoints for a unified Santali language experience."""
from __future__ import annotations
import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import Response

from .santali_translation_service import (
    translate_english_to_santali,
    translate_santali_to_english,
    translation_status,
)
from .santali_tts_service import synthesize_santali_wav, tts_model_loaded

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/tribal-languages/santali",
    tags=["Santali Language"],
)


class SantaliTranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    direction: Literal["santali_to_english", "english_to_santali"]


class SantaliTTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1200)


@router.get("/status")
def santali_language_status() -> dict:
    return {
        "language": "santali",
        "status": "available",
        "translation": translation_status(),
        "tts_model": "kaushalkrishnax/santali-piper-vits",
        "tts_loaded": tts_model_loaded(),
        "note": "Models load lazily on first request. Generated translation and speech require evaluation; this status is not an accuracy claim.",
    }


@router.post("/translate")
def translate(request: SantaliTranslationRequest) -> dict:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Translation input is empty.")
    try:
        if request.direction == "santali_to_english":
            result = translate_santali_to_english(text)
        else:
            result = translate_english_to_santali(text)
        return {
            "success": True,
            "language": "santali",
            "direction": request.direction,
            "translation": result,
            "status": "machine_translation_requires_language_review",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Santali translation failed (%s)", request.direction)
        raise HTTPException(
            status_code=503,
            detail=f"Santali translation is unavailable: {type(exc).__name__}: {exc}",
        ) from exc


@router.post("/tts")
def synthesize(request: SantaliTTSRequest) -> Response:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Santali TTS input is empty.")
    try:
        audio = synthesize_santali_wav(text)
        return Response(
            content=audio,
            media_type="audio/wav",
            headers={"Content-Disposition": 'inline; filename="santali_response.wav"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Santali TTS failed")
        raise HTTPException(
            status_code=503,
            detail=f"Santali speech generation is unavailable: {type(exc).__name__}: {exc}",
        ) from exc
