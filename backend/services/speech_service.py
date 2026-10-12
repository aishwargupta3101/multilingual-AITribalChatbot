import asyncio
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from backend.speech.whisper_service import whisper_service
class SpeechService:
    AUDIO_DIR = Path("data/audio")
    ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}
    LANGUAGE_CODES = {
        "english": "en",
        "hindi": "hi",
        "manipuri": "mni",
        "manipuri_mtei": "mni",
    }
    def __init__(self):
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    async def save_audio(self, file: UploadFile):
        if not file.filename:
            raise HTTPException(status_code=400, detail="Audio filename is missing.")

        extension = Path(file.filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {extension}",
            )

        filename = f"{uuid4().hex}{extension}"
        file_path = self.AUDIO_DIR / filename

        try:
            content = await file.read()

            if not content:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded audio file is empty.",
                )

            file_path.write_bytes(content)

            return {
                "filename": filename,
                "original_filename": Path(file.filename).name,
                "path": str(file_path),
                "status": "saved",
            }

        finally:
            await file.close()

    async def transcribe_audio(self, file: UploadFile, language: str = "english"):
        saved_audio = await self.save_audio(file)
        audio_path = saved_audio["path"]
        language = language.lower().strip()
        whisper_language = self.LANGUAGE_CODES.get(language)
        try:
            result = await asyncio.to_thread(
                whisper_service.transcribe,
                audio_path,
                whisper_language,
            )
            if not result["text"]:
                raise HTTPException(
                    status_code=422,
                    detail="No speech could be detected in the audio.",
                )
            return {
                "success": True,
                "text": result["text"],
                "language": result["language"],
                "language_probability": result["language_probability"],
                "filename": saved_audio["filename"],
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Speech transcription failed.",
            ) from exc
speech_service = SpeechService()