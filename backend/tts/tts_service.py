"""
Text-to-Speech Service
"""

import logging
import os
import tempfile

from gtts import gTTS
logger = logging.getLogger(__name__)

class TTSService:
    LANGUAGE_MAP = {
        "english": "en",
        "hindi": "hi",
    }
    async def generate_speech(
        self,
        text: str,
        language: str = "english"
    ):
        language = (
            language or "english"
        ).lower().strip()
        text = (
            text or ""
        ).strip()
        if not text:
            return {
                "success": False,
                "error": "Text is empty."
            }

        try:
            tts_language = self.LANGUAGE_MAP.get(
                language
            )
            if not tts_language:
                return {
                    "success": False,
                    "error": (
                        f"TTS is not supported for "
                        f"'{language}' yet."
                    )
                }
            fd, audio_file = tempfile.mkstemp(
                suffix=".mp3"
            )
            os.close(fd)
            logger.info("=" * 60)
            logger.info("TTS REQUEST")
            logger.info(
                f"Language: {language}"
            )
            logger.info(
                f"TTS Language: {tts_language}"
            )
            logger.info(
                f"Text: {text}"
            )
            logger.info("=" * 60)
            tts = gTTS(
                text=text,
                lang=tts_language,
                slow=False
            )
            tts.save(audio_file)
            if not os.path.exists(
                audio_file
            ):
                return {
                    "success": False,
                    "error": "TTS audio file was not created."
                }
            file_size = os.path.getsize(
                audio_file
            )

            if file_size == 0:
                return {
                    "success": False,
                    "error": "Generated TTS audio is empty."
                }
            logger.info(
                f"TTS audio created: {audio_file}"
            )
            logger.info(
                f"Audio size: {file_size} bytes"
            )
            return {
                "success": True,
                "audio_file": audio_file,
                "language": language,
                "format": "mp3"
            }
        except Exception as e:
            logger.exception(
                "TTS generation failed."
            )
            return {
                "success": False,
                "error": str(e)
            }
tts_service = TTSService()