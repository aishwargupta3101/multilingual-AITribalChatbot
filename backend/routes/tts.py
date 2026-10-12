
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.api.dependencies import get_tts_service
from backend.schemas.tts import TTSRequest
from backend.services.tts_service import TTSService

router = APIRouter(
    prefix="/tts",
    tags=["TTS"]
)


@router.post("")
async def tts(
    request: TTSRequest,
    tts_service: TTSService = Depends(get_tts_service)
):
    return await tts_service.generate_audio(request)


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    if Path(filename).name != filename or not filename.endswith(".mp3"):
        raise HTTPException(
            status_code=400,
            detail="Invalid audio filename."
        )

    audio_path = TTSService.AUDIO_DIR / filename

    if not audio_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Audio file not found."
        )

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=filename
    )