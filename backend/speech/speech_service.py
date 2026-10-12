
"""
Speech-to-Text Service
"""

import asyncio
import logging
from pathlib import Path

from backend.speech.whisper_service import whisper_service

logger = logging.getLogger(__name__)


class SpeechService:
    LANGUAGE_MAP = {
        "english": "en",
        "hindi": "hi",
        "manipuri": None,
        "manipuri_mtei": None,
    }

    UNSUPPORTED_LANGUAGES = {
        "tai_khamti",
        "monpa",
        "naga",
        "mishmi",
    }

    async def speech_to_text(
        self,
        audio_path: str,
        language: str = "english",
    ):
        language = (language or "english").lower().strip()

        logger.info("=" * 70)
        logger.info("SPEECH TO TEXT")
        logger.info("Audio Path: %s", audio_path)
        logger.info("Selected Language: %s", language)
        logger.info("=" * 70)

        if not audio_path:
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": "Audio path is empty.",
            }

        audio_file = Path(audio_path)

        if not audio_file.is_file():
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": f"Audio file not found: {audio_path}",
            }

        if audio_file.stat().st_size == 0:
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": "Audio file is empty.",
            }

        if language in self.UNSUPPORTED_LANGUAGES:
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": (
                    f"Speech recognition for {language} "
                    "is not supported yet."
                ),
            }
        if language not in self.LANGUAGE_MAP:
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": f"Unsupported language: {language}",
            }
        whisper_language = self.LANGUAGE_MAP[language]
        logger.info("Whisper Language: %s", whisper_language)

        try:
            result = await asyncio.to_thread(
                whisper_service.transcribe,
                str(audio_file),
                language=whisper_language,
            )

            text = str(result.get("text", "")).strip()
            detected_language = result.get("language", language)
            confidence = result.get("language_probability", 0)

            if not text:
                return {
                    "success": False,
                    "text": "",
                    "language": detected_language,
                    "confidence": confidence,
                    "error": "No speech could be detected in the audio.",
                }

            logger.info("Transcription: %s", text)

            return {
                "success": True,
                "text": text,
                "language": detected_language,
                "confidence": confidence,
            }

        except Exception as e:
            logger.exception("Speech Recognition Failed")
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": str(e),
            }
speech_service = SpeechService()