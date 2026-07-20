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
        if source_language == target_language:
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
            raise
    def auto_translate_to_english(
        self,
        text: str
    ):
        """
        Detect language and translate to English.
        """
        language = self.detect_language(text)
        translated_text = self.translate(
            text=text,
            source_language=language,
            target_language="english"
        )
        return {

            "original_text": text,
            "translated_text": translated_text,
            "detected_language": language
        }
    def translate_response(
        self,
        response:str,
        user_language:str
    ):
        """
            Translate chatbot response back to the user's language.
        """
        if user_language == "english":
            return response
        return self.translate(
            text=response,
            source_language="english",
            target_language=user_language
        )
translation_service = TranslationService()





