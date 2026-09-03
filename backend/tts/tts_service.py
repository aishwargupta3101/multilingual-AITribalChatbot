"""
Text-to-Speech Service
"""

import logging

from backend.tts.xtts_service import get_xtts_service
from backend.tts.manipuri_tts import manipuri_tts
logger = logging.getLogger(__name__)


class TTSService:
    async def generate_speech(
        self,
        text: str,
        language: str
    ):
        try:
            language = language.lower().strip()
            print("=" * 60)
            print("Language:", language)

            if language == "manipuri":
                print("Using AI4Bharat Manipuri TTS")
                audio_file = (
                    manipuri_tts.text_to_speech(
                        text=text
                    )
                )
            elif language == "tai_khamti":
                raise NotImplementedError(
                    "Tai Khamti TTS will be added "
                    "after fine-tuning."
                )

            elif language == "monpa":
                raise NotImplementedError(
                    "Monpa TTS will be added "
                    "after fine-tuning."
                )

            elif language == "naga":
                raise NotImplementedError(
                    "Naga TTS will be added "
                    "after fine-tuning."
                )

            elif language == "mishmi":
                raise NotImplementedError(
                    "Mishmi TTS will be added "
                    "after fine-tuning."
                )
            else:
                print("Using existing XTTS service")
                audio_file = (
                    get_xtts_service().text_to_speech(
                        text=text,
                        language=language
                    )
                )

            print("Generated:", audio_file)
            return {
                "success": True,
                "audio_file": audio_file,
                "language": language
            }

        except Exception as e:
            logger.exception(
                "TTS Generation Failed"
            )
            return {
                "success": False,
                "audio_file": None,
                "language": language,
                "error": str(e)
            }

tts_service = TTSService()