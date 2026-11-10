"""Gondi local MT5 + experimental Meta MMS speech API routes."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.tribal_languages.gondi_local_translation_service import gondi_local_translation_service
from backend.tribal_languages.gondi_mms_service import gondi_mms_services

router = APIRouter(prefix="/api/v1/tribal-languages/gondi", tags=["Gondi Language"])


class GondiTranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    direction: Literal["hindi_to_gondi", "gondi_to_hindi"]


class GondiTTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1200)


@router.get("/status")
def gondi_status() -> dict:
    """Return explicit readiness; model weights are loaded only on first inference."""
    mt_status = gondi_local_translation_service.status()
    speech = gondi_mms_services.status()
    return {
        "language": "gondi",
        "variety": "Adilabad Gondi (wsg) for MMS speech models",
        "translation": mt_status,
        "speech": speech,
    }


@router.post("/translate")
def translate_gondi(request: GondiTranslationRequest) -> dict:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Gondi translation input is empty.")
    try:
        translated = gondi_local_translation_service.translate(text, request.direction)
        return {"success": True, "language": "gondi", "direction": request.direction, "translation": translated}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/asr")
async def gondi_asr(audio: UploadFile = File(...)) -> dict:
    """Transcribe WAV/FLAC audio with MMS (experimental, Adilabad Gondi)."""
    if audio.content_type not in {"audio/wav", "audio/x-wav", "audio/flac", "audio/x-flac", "application/octet-stream"}:
        # Some browsers use an unset or generic MIME type, which is accepted above.
        if not (audio.filename or "").lower().endswith((".wav", ".flac")):
            raise HTTPException(status_code=415, detail="Upload a WAV or FLAC recording for Gondi speech recognition.")
    data = await audio.read()
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds the 25 MB limit.")
    try:
        result = gondi_mms_services.transcribe_audio_bytes(data)
        return {"success": True, "language": "gondi", "variety": "Adilabad Gondi (wsg)", **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/tts")
def gondi_tts(request: GondiTTSRequest) -> Response:
    """Synthesize Gondi audio using MMS-TTS-wsg; returns audio/wav."""
    try:
        wav_bytes, speech_text = gondi_mms_services.synthesize_wav(request.text)
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": 'inline; filename="gondi-answer.wav"', "X-Gondi-TTS-Script": "Telugu-script approximation"},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
