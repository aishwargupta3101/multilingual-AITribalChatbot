from fastapi import APIRouter
from backend.schemas.tts import TTSRequest,TTSResponse
from backend.services.tts_services import TTSService
router = APIRouter(
    prefix="/tts",
    tags=["Text to Speech"]
)

@router.post(
    "/",
    response_model=TTSResponse)
async def tts(request: TTSRequest):
    return TTSService.generate_audio(request)