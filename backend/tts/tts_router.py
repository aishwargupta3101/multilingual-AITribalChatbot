from fastapi import APIRouter
from fastapi.responses import FileResponse
import os
from backend.tts.schemas import TTSRequest
from backend.tts.tts_service import tts_service

router = APIRouter(
    prefix="/tts",
    tags=["Text to Speech"]
)

@router.post("/")
async def text_to_speech(request: TTSRequest):

    result = await tts_service.generate_speech(
        text=request.text,
        language=request.language
    )
    print("=" * 60)
    print(result)
    if not result["success"]:
        return result

    print("Audio Path :", result["audio_file"])
    print("Exists     :", os.path.exists(result["audio_file"]))
    print("Size       :", os.path.getsize(result["audio_file"]))
    print("=" * 60)
    return FileResponse(
        path=result["audio_file"],
        media_type="audio/wav",
        filename="response.wav"
    )