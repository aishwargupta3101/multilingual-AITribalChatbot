import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Form
from .speech_service import speech_service

router = APIRouter(
    prefix="/api/v1/speech",
    tags=["Speech"]
)

@router.post("")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form("english")
):
    suffix = os.path.splitext(audio.filename)[1]
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:

        shutil.copyfileobj(audio.file, temp)
        temp_path = temp.name
    result = await speech_service.speech_to_text(
        audio_path=temp_path,
        language=language
    )
    os.remove(temp_path)
    return result