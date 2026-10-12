
import asyncio
from pathlib import Path
from uuid import uuid4
from gtts import gTTS
from fastapi import HTTPException
from backend.schemas.tts import TTSRequest
from backend.utils.response import ResponseBuilder


class TTSService:
    AUDIO_DIR = Path("data/audio/output")
    LANGUAGE_CODES = {
        "english": "en",
        "hindi": "hi",
    }

    def __init__(self):
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    async def generate_audio(self, request: TTSRequest):
        text = request.text.strip()
        language = request.language.lower().strip()

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty.",
            )

        language_code = self.LANGUAGE_CODES.get(language)

        if not language_code:
            raise HTTPException(
                status_code=400,
                detail=f"TTS is not currently supported for {language}.",
            )

        filename = f"{uuid4().hex}.mp3"
        audio_path = self.AUDIO_DIR / filename

        try:
            await asyncio.to_thread(
                self._generate_file,
                text,
                language_code,
                audio_path,
            )

            return ResponseBuilder.success(
                message="Audio generated successfully.",
                data={
                    "audio_path": str(audio_path),
                    "filename": filename,
                    "language": language,
                    "status": "generated",
                },
            )
        except Exception as exc:
            audio_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500,
                detail="Failed to generate audio.",
            ) from exc
    @staticmethod
    def _generate_file(text, language_code, audio_path):
        gTTS(text=text, lang=language_code, slow=False).save(str(audio_path))
tts_service = TTSService()