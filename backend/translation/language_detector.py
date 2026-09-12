"""
Language Detection Module
"""

import re

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
DetectorFactory.seed = 0

class LanguageDetector:
    """
    Detect the language of the user input.
    """
    LANGUAGE_MAPPING = {
        "en": "english",
        "hi": "hindi",
        "mni": "manipuri",
    }
    TAI_KHAMTI_WORDS = {
        "mi",
        "yu",
        "ma",
        "kow",
        "ti",
        "ka",
        "non",
        "hai",
        "phaik",
        "pa",
        "atit",
        "nei",
        "wan",
        "pheng",
        "man",
        "nai",
        "nam",
        "din",
        "li",
    }
    TAI_KHAMTI_SCRIPT_PATTERN = re.compile(
        r"[\u1000-\u109F]"
    )

    LATIN_WORD_PATTERN = re.compile(
        r"[a-zA-Z]+"
    )
    @classmethod
    def _is_tai_khamti_transliteration(
        cls,
        text: str
    ) -> bool:
        words = cls.LATIN_WORD_PATTERN.findall(
            text.lower()
        )
        if not words:
            return False
        matches = sum(
            word in cls.TAI_KHAMTI_WORDS
            for word in words
        )
        return matches >= 2

    @classmethod
    def _is_tai_khamti_script(
        cls,
        text: str
    ) -> bool:
        matches = cls.TAI_KHAMTI_SCRIPT_PATTERN.findall(
            text
        )
        return len(matches) >= 2

    @classmethod
    def detect_language(
        cls,
        text: str
    ) -> str:
        if not text or not text.strip():
            return "english"
        text = text.strip()
        if cls._is_tai_khamti_script(text):
            return "tai_khamti"
        if cls._is_tai_khamti_transliteration(text):
            return "tai_khamti"
        try:
            detected_code = detect(text)
            return cls.LANGUAGE_MAPPING.get(
                detected_code,
                "english"
            )
        except LangDetectException:
            return "english"
language_detector = LanguageDetector()