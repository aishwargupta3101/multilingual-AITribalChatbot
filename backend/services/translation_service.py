"""
Translation Service
"""
import logging

from backend.translation.language_detector import LanguageDetector
from backend.translation.nllb_service import nllb_service

logger = logging.getLogger(__name__)
class TranslationService:
    """
    Handles all Translation-related business logic.
    """
    def __init__(self):
        self.translator = nllb_service

    def detect_language(self,text:str) -> str:
        """
        Detect the language of the input text.
        """
        return LanguageDetector.detect_language(text)
    def translate(
        self,
        text:str,
        source_language:str,
        target_language:str
    )-> str:
        """
        Translate text between two language.
        """
        if not text.strip():
            return ""
        if source_language.lower() == target_language.lower():
            return text
        try:
            translated_text = self.translator.translate(
                text=text,
                source_language=source_language,
                target_language=target_language
            )
            logger.info(
                f"{source_language} -> {target_language}"
            )
            return translated_text
        except Exception as e:
            logger.error(
                f"TranslationError:{e}"
            )
            return text
    def auto_translate_to_english(
        self,
        text: str
    ) -> dict:
        """
        Detect language and translate to English.
        """
        detected_language = self.detect_language(text)
        if detected_language.lower() == "english":
            return{
                "detected_language": "english",
                "translated_text":text
            }
        try:

            translated = self.translate(
                text=text,
                source_language=detected_language,
                target_language="english"
            )
        except Exception as e:
            logger.error(
                f"Translation Error: {e}"
            )
            translated = text
        return {
            "detected_language": detected_language,
            "translated_text":translated
        }
    def translate_response(
        self,
        response:str,
        user_language:str
    ) -> str:
        """
            Translate the English response back to the user's language.
        """
        if not response:
            return ""
        if user_language.lower() == "english":
            return response
        try:
            translated = self.translate(
                text=response,
                source_language="english",
                target_language=user_language
            )
            return translated
        except Exception as e:
            logger.error(
                f"Response Translation Error : {e}"
            )
            return response
translation_service = TranslationService()





