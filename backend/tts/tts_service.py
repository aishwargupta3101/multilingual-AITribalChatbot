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
            print("=" * 60)
            print("Original Language:", repr(language))
            language = language.lower().strip()
            print("Processed Language:", repr(language))
            if language == "manipuri":
                print("✅ USING MANIPURI TTS")
                audio_file = manipuri_tts.text_to_speech(
                    text=text
                )

            else:
                print("❌ USING XTTS")
                audio_file = get_xtts_service.text_to_speech(
                    text=text,
                    language=language
                )
            print("Generated:", audio_file)
            print("=" * 60)

            return {
                "success": True,
                "audio_file": audio_file,
                "language": language
            }

        except Exception as e:
            logger.exception("TTS Generation Failed")
            return {
                "success": False,
                "audio_file": None,
                "language": language,
                "error": str(e)
            }

tts_service = TTSService()