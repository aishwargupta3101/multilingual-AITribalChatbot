from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from fastapi import APIRouter, File, UploadFile, Form, Depends
from backend.services.speech_service import SpeechService, speech_service
router = APIRouter(prefix="/speech", tags=["Speech"])
def get_speech_service():
    return speech_service
@router.post("/upload")
async def upload_audio(
    audio: UploadFile = File(None),
    file: UploadFile = File(None),
    service: SpeechService = Depends(get_speech_service),
):
    uploaded_file = audio or file
    if uploaded_file is None:
        raise HTTPException(
            status_code=400,
            detail="Audio file is missing. Send the file using 'audio' or 'file'."
        )
    return await service.save_audio(uploaded_file)
@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("english"),
    service: SpeechService = Depends(get_speech_service),
):
    return await service.transcribe_audio(file, language)