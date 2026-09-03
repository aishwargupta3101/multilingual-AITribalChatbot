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
        "yu",
    }
    @classmethod
    def _is_tai_khamti_transliteration(cls, text: str) -> bool:
        """
        Detect common Latin-script Tai Khamti transliteration.
        """
        words = re.findall(
            r"[a-zA-Z]+",
            text.lower()
        )
        if not words:
            return False
        tai_khamti_matches = sum(
            1
            for word in words
            if word in cls.TAI_KHAMTI_WORDS
        )
        if tai_khamti_matches >= 2:
            return True
        return False

    @classmethod
    def _is_tai_khamti_script(cls, text: str) -> bool:
        """
        Detect Tai/Shan-style Unicode characters used
        in the Tai Khamti dataset.
        """
        tai_characters = re.findall(
            r"[\u1000-\u109F]",
            text
        )
        return len(tai_characters) >= 2
    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detect the language of the input text.

        Args:
            text: User input text

        Returns:
            Language name
        """
        if not text or text.strip() == "":
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