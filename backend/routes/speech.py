from fastapi import APIRouter,File,UploadFile
from backend.services.speech_service import SpeechService
from backend.services.speech_service import SpeechService
router = APIRouter()
speech_services =SpeechService()

@router.post("/upload")
async def upload_audio(file:UploadFile = File(...)):
    return await speech_services.save_audio(file)