"""
Text-to-Speech Service
"""
import logging
from backend.tts.seamless_tts_service import (
    seamless_tts_service
)
logger =logging.getLogger(__name__)
class TTSService:
    """
    Handles Text-to-Speech requests.
    """
    async def generate_speech(
        self,
        text:str,
        language:str
    ):
        try:
            audio_file =(
                seamless_tts_service.text_to_speech(
                    text=text,
                    language=language
                )
            )
            return {
                "success":False,
                "audio_file":None,
                "language":language
            }
        except Exception as e:
            logger.exception("TTS Generation Failed")
        return {
            "success":False,
            "audio_file":None,
            "language":language,
            "error":str(e)
        }
tts_service = TTSService()

