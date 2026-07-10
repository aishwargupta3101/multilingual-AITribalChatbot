from fastapi import APIRouter, Depends
from backend.api.dependencies import get_speech_service
from backend.schemas.speech import SpeechRequest
from backend.services.speech_service import SpeechService
router = APIRouter(
    prefix="/speech",
    tags=["Speech"]
)

@router.post("/")
async def speech(
    request: SpeechRequest,
    speech_service: SpeechService = Depends(get_speech_service)
):
    return await speech_service.speech_to_text(request)