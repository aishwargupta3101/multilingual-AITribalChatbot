"""
Language Detection Module
"""

from langdetect import detect,DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed=0

class LanguageDetector:
    """
    Detect the language of the user input.
    """
    LANGUAGE_MAPPING ={
        "en":"english",
        "hi":"hindi",
        "sat":"santali",
        "gon":"gondi",
        "trp":"kokborok"
    }
    @classmethod
    def detect_language(cls,text:str) -> str:
        """
        Detect the language of the input text.
        Args:
            text: User input text
        Returns:
            Language name (english, hindi,etc)
        """
        if not text or text.strip() =="":
            return "english"
        try:
            detected_code = detect(text)
            return cls.LANGUAGE_MAPPING.get(
                detected_code,
                "english"
            )
        except LangDetectException:
            return "english"