import os
import shutil
import tempfile

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)
from .speech_service import speech_service
router = APIRouter(
    prefix="/api/v1/speech",
    tags=["Speech"]
)
@router.post("/upload")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form("english")
):
    temp_path = None
    try:
        suffix = os.path.splitext(
            audio.filename or ".wav"
        )[1]
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp:
            shutil.copyfileobj(
                audio.file,
                temp
            )
            temp_path = temp.name
        result = await speech_service.speech_to_text(
            audio_path=temp_path,
            language=language
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "language": language,
            "confidence": 0,
            "error": str(e)
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass