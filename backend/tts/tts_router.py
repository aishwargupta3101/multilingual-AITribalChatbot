import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from backend.tts.schemas import TTSRequest
from backend.tts.tts_service import tts_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tts", tags=["Text to Speech"])


@router.post("")
async def text_to_speech(request: TTSRequest):
    result = await tts_service.generate_speech(text=request.text, language=request.language)
    if not result.get("success"):
        logger.error("TTS request failed: %s", result.get("error"))
        raise HTTPException(status_code=502, detail=result.get("error", "TTS generation failed."))

    audio_path = result["audio_file"]
    if not os.path.isfile(audio_path) or os.path.getsize(audio_path) == 0:
        raise HTTPException(status_code=502, detail="TTS output file is missing or empty.")

    audio_format = result.get("format", Path(audio_path).suffix.lstrip(".")).lower()
    media_type = "audio/wav" if audio_format == "wav" else "audio/mpeg"
    return FileResponse(
        path=audio_path,
        media_type=media_type,
        filename=f"tribal_ai_speech.{audio_format}",
        background=BackgroundTask(lambda: os.path.exists(audio_path) and os.remove(audio_path)),
    )
