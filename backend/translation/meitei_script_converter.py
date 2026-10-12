"""
Manipuri Script Conversion Service
Bengali Script <-> Meitei Mayek
"""
import logging
import sys
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)


class MeiteiScriptConverter:
    """Converts Manipuri text between Bengali script and Meitei Mayek."""

    def __init__(self):
        self._bengali_to_meitei = None
        self._meitei_to_bengali = None

    def _load_bengali_to_meitei(self):
        if self._bengali_to_meitei is not None:
            return
        try:
            xlit_path = Path(__file__).resolve().parents[2] / "xlit"
            if str(xlit_path) not in sys.path:
                sys.path.insert(0, str(xlit_path))
            from src.mt_ import MTransliteration
            self._bengali_to_meitei = MTransliteration()
            logger.info("Bengali-to-Meitei converter loaded.")
        except ImportError as error:
            logger.exception("Failed to load Bengali-to-Meitei converter.")
            raise ImportError(
                "XLIT dependency is missing. Check the XLIT installation."
            ) from error

    def _load_meitei_to_bengali(self):
        if self._meitei_to_bengali is not None:
            return
        try:
            from mtei2bangla import MeiteitoBangla
            self._meitei_to_bengali = MeiteitoBangla
            logger.info("Meitei-to-Bengali converter loaded.")
        except ImportError as error:
            logger.exception("Failed to load Meitei-to-Bengali converter.")
            raise ImportError(
                "Install the meiteitobangla dependency."
            ) from error

    @lru_cache(maxsize=512)
    def convert_bengali_to_meitei(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        self._load_bengali_to_meitei()
        converted_words = []
        for word in text.strip().split():
            has_bengali = any("\u0980" <= char <= "\u09FF" for char in word)
            if not has_bengali:
                converted_words.append(word)
                continue
            try:
                converted = self._bengali_to_meitei.transliterate(word)
                converted_words.append(converted if converted else word)
            except IndexError:
                logger.warning("XLIT could not convert token; preserving: %s", word)
                converted_words.append(word)
        result = " ".join(converted_words)
        if not result.strip():
            raise ValueError("Bengali-to-Meitei conversion returned empty text.")
        return result

    @lru_cache(maxsize=512)
    def convert_meitei_to_bengali(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        self._load_meitei_to_bengali()
        try:
            result = self._meitei_to_bengali.transliterate(text.strip())
            if not result:
                raise ValueError("Meitei-to-Bengali conversion returned empty text.")
            return result.strip()
        except Exception:
            logger.exception("Meitei-to-Bengali conversion failed.")
            raise


meitei_script_converter = MeiteiScriptConverter()


def convert_bengali_to_meitei(text: str) -> str:
    return meitei_script_converter.convert_bengali_to_meitei(text)


def convert_meitei_to_bengali(text: str) -> str:
    return meitei_script_converter.convert_meitei_to_bengali(text)
