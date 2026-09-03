"""
Translation Service
"""

import logging

from backend.translation.language_detector import LanguageDetector
from backend.translation.nllb_service import nllb_service

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Handles all translation-related business logic.
    """
    def __init__(self):
        self.translator = nllb_service
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        """
        return LanguageDetector.detect_language(text)
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        if not text or not text.strip():
            return ""
        source_language = source_language.lower().strip()
        target_language = target_language.lower().strip()
        if source_language == target_language:
            return text
        try:
            translated_text = self.translator.translate(
                text=text,
                source_language=source_language,
                target_language=target_language
            )

            logger.info(
                f"Translation completed: "
                f"{source_language} -> {target_language}"
            )
            logger.info(
                f"Translated text: {translated_text}"
            )
            return translated_text
        except Exception as e:
            logger.exception(
                f"Translation failed: "
                f"{source_language} -> {target_language}"
            )
            raise e
    def auto_translate_to_english(
        self,
        text: str
    ) -> dict:
        detected_language = self.detect_language(text)
        detected_language = (
            detected_language.lower().strip()
        )
        logger.info(
            f"Detected language: {detected_language}"
        )
        if detected_language == "english":
            return {
                "detected_language": "english",
                "translated_text": text
            }
        try:
            translated = self.translate(
                text=text,
                source_language=detected_language,
                target_language="english"
            )
            return {
                "detected_language": detected_language,
                "translated_text": translated
            }
        except Exception as e:
            logger.exception(
                f"Auto translation to English failed: {e}"
            )
            return {
                "detected_language": detected_language,
                "translated_text": text
            }
    def translate_response(
        self,
        response: str,
        user_language: str
    ) -> str:
        if not response:
            return ""
        user_language = (
            user_language.lower().strip()
        )
        logger.info(
            f"Translating response to: "
            f"{user_language}"
        )
        if user_language == "english":
            return response
        try:
            translated = self.translate(
                text=response,
                source_language="english",
                target_language=user_language
            )
            if not translated:
                logger.warning(
                    "Translation returned empty text."
                )
                return response
            if translated.strip() == response.strip():
                logger.warning(
                    f"Translation returned original text: "
                    f"English -> {user_language}"
                )
            return translated
        except Exception as e:

            logger.exception(
                f"Response translation failed: "
                f"English -> {user_language}"
            )

            return response
translation_service = TranslationService()