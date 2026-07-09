from fastapi import APIRouter
from backend.services.speech_service import SpeechService
from backend.schemas.speech import SpeechRequest,SpeechResponse
router= APIRouter(
    prefix="/speech",
    tags=["Speech"]
)
@router.post(
    "/",
    response_model=SpeechResponse)
async def speech (request:SpeechRequest):
    return await SpeechService.speech_to_text(request)

