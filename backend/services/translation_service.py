
import logging
import re
from functools import lru_cache
from backend.translation.indictrans_service import indictrans_service
from backend.translation.nllb_service import nllb_service
from backend.translation.meitei_script_converter import meitei_script_converter
from backend.services.sarvam_translation_service import sarvam_translation_service
logger = logging.getLogger(__name__)

class TranslationService:
    """Centralized translation service supporting English, Hindi, and both Manipuri scripts."""

    LANGUAGE_ALIASES = {
        "en": "english",
        "eng": "english",
        "hi": "hindi",
        "hin": "hindi",
        "meitei": "manipuri",
        "mni": "manipuri",
        "mni_beng": "manipuri",
        "manipuri_beng": "manipuri",
        "manipuri_bengali": "manipuri",
        "manipuri_meitei": "manipuri_mtei",
        "meitei_mayek": "manipuri_mtei",
        "manipuri_mtei": "manipuri_mtei",
        "mni_mtei": "manipuri_mtei"
    }

    SUPPORTED_LANGUAGES = {
        "english",
        "hindi",
        "manipuri",
        "manipuri_mtei"
    }

    def __init__(self):
        self.indictrans = indictrans_service
        self.nllb = nllb_service

    @classmethod
    def normalize_language(cls, language):
        if not language:
            raise ValueError("Language cannot be empty.")
        language = str(language).lower().strip().replace("-", "_").replace(" ", "_")
        return cls.LANGUAGE_ALIASES.get(language, language)

    @classmethod
    def validate_language(cls, language):
        if language not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")

    @staticmethod
    def _validate_text(text):
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")
        return text.strip()

    def _translate_uncached(self, text, source_language, target_language):
        if source_language == target_language:
            return text

        # English, Hindi, or Manipuri Bengali -> Meitei Mayek
        if target_language == "manipuri_mtei":

            # Hindi -> English -> Manipuri Bengali
            if source_language == "hindi":
                english_text = self.indictrans.translate(
                    text=text,
                    source_language="hindi",
                    target_language="english"
                )

                bengali_text = self.nllb.translate(
                    text=english_text,
                    source_language="english",
                    target_language="manipuri"
                )

            # English -> Manipuri (Meitei Mayek): prefer Sarvam when configured.
            # On any API/configuration failure, preserve the existing NLLB route.
            elif source_language == "english":
                if sarvam_translation_service.is_configured():
                    try:
                        return sarvam_translation_service.translate_english_to_manipuri_mtei(text)
                    except Exception:
                        logger.exception(
                            "Sarvam English-to-Manipuri translation failed; falling back to existing NLLB route."
                        )
                bengali_text = self.nllb.translate(
                    text=text,
                    source_language="english",
                    target_language="manipuri"
                )

            # Manipuri Bengali -> Meitei Mayek
            elif source_language == "manipuri":
                bengali_text = text

            else:
                raise ValueError(
                    f"Unsupported source language for Meitei Mayek: {source_language}"
                )

            result = meitei_script_converter.convert_bengali_to_meitei(
                bengali_text
            )

        # Meitei Mayek -> English, Hindi, or Manipuri Bengali
        elif source_language == "manipuri_mtei":

            # First convert Meitei Mayek -> Manipuri Bengali
            bengali_text = meitei_script_converter.convert_meitei_to_bengali(
                text
            )

            # Manipuri Bengali -> English
            if target_language == "english":
                result = self.nllb.translate(
                    text=bengali_text,
                    source_language="manipuri",
                    target_language="english"
                )

            # Manipuri Bengali -> English -> Hindi
            elif target_language == "hindi":
                english_text = self.nllb.translate(
                    text=bengali_text,
                    source_language="manipuri",
                    target_language="english"
                )

                result = self.indictrans.translate(
                    text=english_text,
                    source_language="english",
                    target_language="hindi"
                )

            # Meitei Mayek -> Manipuri Bengali
            elif target_language == "manipuri":
                result = bengali_text

            else:
                raise ValueError(
                    f"Unsupported target language: {target_language}"
                )

        # Hindi -> Manipuri Bengali: use English as an intermediate language.
        elif source_language == "hindi" and target_language == "manipuri":
            english_text = self.indictrans.translate(
                text=text,
                source_language="hindi",
                target_language="english"
            )

            result = self.nllb.translate(
                text=english_text,
                source_language="english",
                target_language="manipuri"
            )
        elif source_language == "manipuri" or target_language == "manipuri":
            result = self.nllb.translate(
                text=text,
                source_language=source_language,
                target_language=target_language
            )
        else:
            result = self.indictrans.translate(
                text=text,
                source_language=source_language,
                target_language=target_language
            )

        if not result or not result.strip():
            raise ValueError(
                f"Translation returned empty output: "
                f"{source_language} -> {target_language}"
            )

        return result.strip()
    @lru_cache(maxsize=1000)
    def _translate_cached(self, text, source_language, target_language):
        return self._translate_uncached(text, source_language, target_language)

    def translate(self, text, source_language, target_language):
        text = self._validate_text(text)
        if not text:
            return ""

        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)

        self.validate_language(source_language)
        self.validate_language(target_language)

        if source_language == target_language:
            return text

        try:
            return self._translate_cached(
                text,
                source_language,
                target_language
            )
        except Exception:
            logger.exception(
                "Translation failed: %s -> %s",
                source_language,
                target_language
            )
            raise

    def auto_translate_to_english(self, text, source_language):
        source_language = self.normalize_language(source_language)
        if source_language == "english":
            return self._validate_text(text)
        return self.translate(text, source_language, "english")

    @staticmethod
    def _split_translation_chunks(text, max_chars=280):
        """Split text at paragraph/sentence boundaries without losing content."""
        text = str(text or "").strip()
        if not text:
            return []
        chunks = []
        # Split on actual blank lines (not the literal characters backslash+n).
        paragraphs = re.split(r"\n\s*\n", text)
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            current = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(sentence) > max_chars:
                    words = sentence.split()
                    piece = ""
                    for word in words:
                        candidate = f"{piece} {word}".strip()
                        if piece and len(candidate) > max_chars:
                            if current:
                                chunks.append(current)
                                current = ""
                            chunks.append(piece)
                            piece = word
                        else:
                            piece = candidate
                    if piece:
                        candidate = f"{current} {piece}".strip()
                        if current and len(candidate) > max_chars:
                            chunks.append(current)
                            current = piece
                        else:
                            current = candidate
                    continue
                candidate = f"{current} {sentence}".strip()
                if current and len(candidate) > max_chars:
                    chunks.append(current)
                    current = sentence
                else:
                    current = candidate
            if current:
                chunks.append(current)
        return chunks

    def translate_response(self, text, target_language, source_language="english"):
        """Translate a response using the original, non-chunked behavior.

        Keep this method unchanged in behavior for normal typed chat.
        Voice-specific callers should use translate_response_for_voice().
        """
        return self.translate(text, source_language, target_language)

    def translate_response_for_voice(self, text, target_language, source_language="english"):
        """Translate long voice responses in chunks while preserving all source content."""
        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)
        text = self._validate_text(text)
        if not text or source_language == target_language:
            return text
        if source_language == "english" and target_language in {"manipuri", "manipuri_mtei"}:
            chunks = self._split_translation_chunks(text, max_chars=280)
            if len(chunks) <= 1:
                return self.translate(text, source_language, target_language)
            translated_chunks = []
            for index, chunk in enumerate(chunks, start=1):
                try:
                    translated = self.translate(chunk, source_language, target_language)
                    if not translated or not translated.strip():
                        raise ValueError("Translation returned empty output.")
                    translated_chunks.append(translated.strip())
                except Exception:
                    logger.exception(
                        "Voice response translation chunk %s/%s failed; preserving source chunk.",
                        index,
                        len(chunks),
                    )
                    # Keep content rather than silently dropping a failed chunk.
                    translated_chunks.append(chunk)
            result = "\n\n".join(translated_chunks).strip()
            logger.info(
                "Voice response chunking completed | Source chars: %s | Chunks: %s | Output chars: %s",
                len(text),
                len(chunks),
                len(result),
            )
            return result
        return self.translate(text, source_language, target_language)

    def clear_cache(self):
        self._translate_cached.cache_clear()
        self.indictrans.clear_cache()
        self.nllb.clear_cache()
        logger.info("Translation caches cleared.")

translation_service = TranslationService()