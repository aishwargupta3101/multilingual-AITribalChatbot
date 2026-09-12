"""
Speech-to-Text Service
"""

import logging
from pathlib import Path
from backend.speech.whisper_service import whisper_service
logger = logging.getLogger(__name__)

class SpeechService:
    LANGUAGE_MAP = {
        "english": "en",
        "hindi": "hi",
        "manipuri": "None",
    }

    async def speech_to_text(
        self,
        audio_path: str,
        language: str = "english"
    ):
        language = (
            language or "english"
        ).lower().strip()
        logger.info("=" * 70)
        logger.info("SPEECH TO TEXT")
        logger.info(f"Audio Path: {audio_path}")
        logger.info(f"Selected Language: {language}")
        logger.info("=" * 70)

        try:
            if not audio_path:
                return {
                    "success": False,
                    "text": "",
                    "language": language,
                    "confidence": 0,
                    "error": "Audio path is empty."
                }

            audio_file = Path(audio_path)
            if not audio_file.exists():
                return {
                    "success": False,
                    "text": "",
                    "language": language,
                    "confidence": 0,
                    "error": (
                        f"Audio file not found: "
                        f"{audio_path}"
                    )
                }
            if audio_file.stat().st_size == 0:
                return {
                    "success": False,
                    "text": "",
                    "language": language,
                    "confidence": 0,
                    "error": "Audio file is empty."
                }
            unsupported_languages = {
                "tai_khamti",
                "monpa",
                "naga",
                "mishmi"
            }

            if language in unsupported_languages:
                return {
                    "success": False,
                    "text": "",
                    "language": language,
                    "confidence": 0,
                    "error": (
                        f"Speech recognition for "
                        f"{language} is not supported yet."
                    )
                }

            whisper_language = self.LANGUAGE_MAP.get(
                language
            )
            logger.info(
                f"Whisper Language: "
                f"{whisper_language}"
            )

            if whisper_language:
                result = whisper_service.transcribe(
                    str(audio_file),
                    language=whisper_language
                )

            else:
                result = whisper_service.transcribe(
                    str(audio_file)
                )
            text = (
                result.get("text", "")
                if isinstance(result, dict)
                else ""
            )
            detected_language = (
                result.get(
                    "language",
                    language
                )
                if isinstance(result, dict)
                else language
            )
            confidence = (
                result.get(
                    "language_probability",
                    0
                )
                if isinstance(result, dict)
                else 0
            )
            text = str(text).strip()
            if not text:
                return {
                    "success": False,
                    "text": "",
                    "language": detected_language,
                    "confidence": confidence,
                    "error": (
                        "No speech could be detected "
                        "in the audio."
                    )
                }
            logger.info(
                f"Transcription: {text}"
            )
            return {
                "success": True,
                "text": text,
                "language": detected_language,
                "confidence": confidence
            }
        except Exception as e:
            logger.exception(
                "Speech Recognition Failed"
            )
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": str(e)
            }
speech_service = SpeechService()