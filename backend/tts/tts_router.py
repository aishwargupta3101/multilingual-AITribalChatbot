from fastapi import APIRouter
from fastapi.responses import FileResponse
import os
from backend.tts.schemas import TTSRequest
from backend.tts.tts_service import tts_service

router = APIRouter(
    prefix="/api/v1/tts",
    tags=["Text to Speech"]
)
@router.post("")
async def text_to_speech(
    request: TTSRequest
):
    result = await tts_service.generate_speech(
        text=request.text,
        language=request.language
    )
    print("=" * 60)
    print("TTS RESULT")
    print(result)
    if not result["success"]:
        return result
    audio_path = result["audio_file"]
    print(
        "Audio Path:",
        audio_path
    )
    print(
        "Exists:",
        os.path.exists(audio_path)
    )
    if os.path.exists(audio_path):
        print(
            "Size:",
            os.path.getsize(audio_path)
        )
    print("=" * 60)
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename="response.mp3"
    )