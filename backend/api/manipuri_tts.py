from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.experimental_voice.indic_tts_bridge import generate_manipuri_tts
from backend.services.response_formatter import format_for_voice

router = APIRouter(
    prefix="/manipuri-tts",
    tags=["Manipuri TTS"]
)

class ManipuriTTSRequest(BaseModel):
    text: str
    script: str = "bengali"
    speaker: str = "female"

@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AI4Bharat Manipuri TTS",
        "scripts": ["bengali", "meitei_mayek"],
        "speakers": ["female", "male"]
    }

@router.post("")
def generate_tts(request: ManipuriTTSRequest):
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    if request.script not in {"bengali", "meitei_mayek"}:
        raise HTTPException(
            status_code=400,
            detail="Script must be bengali or meitei_mayek."
        )
    if request.speaker not in {"female", "male"}:
        raise HTTPException(
            status_code=400,
            detail="Speaker must be female or male."
        )

    try:
        voice_text = format_for_voice(request.text, "manipuri")
        if not voice_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty after formatting."
            )
        audio_path = generate_manipuri_tts(
            text=voice_text,
            script=request.script,
            speaker=request.speaker
        )
        return FileResponse(
            path=str(audio_path),
            media_type="audio/wav",
            filename="manipuri_ai4bharat.wav"
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )