"""
Text-to Speech API Router
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
from backend.tts.schemas import TTSRequest
from backend.tts.tts_service import tts_service

router = APIRouter(
    prefix="/tts",
    tags=["Text to Speech"]
)
@router.post("/")
async def text_to_speech(request: TTSRequest):
    result = await  tts_service.generate_speech(
        text=request.text,
        language=request.language
    )
    if not result["success"]:
        return result
    return FileResponse(
        path=result["audio_file"],
        media_type="audio/wav",
        filename="response.wav"
    )