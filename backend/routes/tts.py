from fastapi import APIRouter, Depends
from backend.api.dependencies import get_tts_service
from backend.schemas.tts import TTSRequest
from backend.services.tts_service import TTSService
router = APIRouter(
    prefix="/tts",
    tags=["TTS"]
)

@router.post("/")
async def tts(
    request: TTSRequest,
    tts_service: TTSService = Depends(get_tts_service)
):
    return await tts_service.generate_audio(request)