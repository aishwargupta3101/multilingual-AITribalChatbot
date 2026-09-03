"""
Speech-to-Text Service
"""

import logging
from backend.speech.whisper_service import whisper_service
logger = logging.getLogger(__name__)


class SpeechService:

    async def speech_to_text(
        self,
        audio_path: str,
        language: str = "english"
    ):
        language = language.lower().strip()

        try:
            if language == "tai_khamti":
                raise NotImplementedError(
                    "Tai Khamti STT will be added after fine-tuning."
                )
            elif language == "monpa":
                raise NotImplementedError(
                    "Monpa STT will be added after fine-tuning."
                )
            elif language == "naga":

                raise NotImplementedError(
                    "Naga STT will be added after fine-tuning."
                )
            elif language == "mishmi":
                raise NotImplementedError(
                    "Mishmi STT will be added after fine-tuning."
                )
            else:
                result = whisper_service.transcribe(audio_path)
            return {
                "success": True,
                "text": result["text"],
                "language": result["language"],
                "confidence": result["language_probability"]
            }
        except Exception as e:
            logger.exception("Speech Recognition Failed")
            return {
                "success": False,
                "text": "",
                "language": language,
                "confidence": 0,
                "error": str(e)
            }
speech_service = SpeechService()