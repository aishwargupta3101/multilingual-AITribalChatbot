"""
Translation Service
"""

import logging
from functools import lru_cache

from backend.translation.language_detector import LanguageDetector
from backend.translation.nllb_service import nllb_service


logger = logging.getLogger(__name__)


class TranslationService:
    """
    Handles translation and language detection.

    Optimizations:
    - Avoid unnecessary translation.
    - Cache repeated translations.
    - Avoid verbose translation logging.
    """
    def __init__(self):
        self.translator = nllb_service
    def detect_language(self, text: str) -> str:
        if not text or not text.strip():
            return "english"
        return (
            LanguageDetector
            .detect_language(text)
            .lower()
            .strip()
        )

    @lru_cache(maxsize=1000)
    def _translate_cached(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        return self.translator.translate(
            text=text,
            source_language=source_language,
            target_language=target_language
        )
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        if not text or not text.strip():
            return ""
        text = text.strip()
        source_language = (
            source_language.lower().strip()
        )
        target_language = (
            target_language.lower().strip()
        )
        if source_language == target_language:
            return text

        try:
            translated_text = self._translate_cached(
                text,
                source_language,
                target_language
            )
            logger.info(
                "Translation completed: %s -> %s",
                source_language,
                target_language
            )
            return translated_text
        except Exception:
            logger.exception(
                "Translation failed: %s -> %s",
                source_language,
                target_language
            )
            raise
    def auto_translate_to_english(
        self,
        text: str
    ) -> dict:
        if not text or not text.strip():
            return {
                "detected_language": "english",
                "translated_text": ""
            }
        detected_language = self.detect_language(text)
        logger.info(
            "Detected language: %s",
            detected_language
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
                "Auto translation to English failed: %s",
                e
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
            return translated
        except Exception:
            logger.exception(
                "Response translation failed: English -> %s",
                user_language
            )
            return response
translation_service = TranslationService()