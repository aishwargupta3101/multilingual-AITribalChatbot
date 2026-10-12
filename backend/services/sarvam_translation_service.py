"""Optional Sarvam translation adapter with safe chunking for long responses."""
import logging
import os
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

class SarvamTranslationService:
    """Translate English to Manipuri (Meitei Mayek) via Sarvam."""
    MAX_CHARS = 1800  # Stay below the API's 2000-character limit.
    def __init__(self):
        self._client = None

    def is_configured(self):
        return bool(os.getenv("SARVAM_API_KEY", "").strip())

    def _get_client(self):
        if self._client is None:
            key = os.getenv("SARVAM_API_KEY", "").strip()
            if not key:
                raise RuntimeError("SARVAM_API_KEY is not configured")
            from sarvamai import SarvamAI
            self._client = SarvamAI(api_subscription_key=key, timeout=30.0)
        return self._client

    @staticmethod
    def _split_text(text, max_chars=1800):
        """Split at paragraph/sentence/word boundaries without dropping text."""
        text = str(text or "").strip()
        if not text:
            return []
        chunks = []
        # Preserve paragraph separation where possible.
        paragraphs = re.split(r"\n\s*\n", text)
        current = ""

        def add_piece(piece):
            nonlocal current
            piece = piece.strip()
            if not piece:
                return
            candidate = f"{current}\n\n{piece}".strip() if current else piece
            if len(candidate) <= max_chars:
                current = candidate
                return
            if current:
                chunks.append(current)
                current = ""
            if len(piece) <= max_chars:
                current = piece
                return
            # Very long paragraph: split by sentences, then words.
            sentences = re.split(r"(?<=[.!?])\s+", piece)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(sentence) > max_chars:
                    words = sentence.split()
                    fragment = ""
                    for word in words:
                        candidate = f"{fragment} {word}".strip()
                        if fragment and len(candidate) > max_chars:
                            if current:
                                chunks.append(current)
                                current = ""
                            chunks.append(fragment)
                            fragment = word
                        else:
                            fragment = candidate
                    if fragment:
                        if current:
                            candidate = f"{current} {fragment}"
                            if len(candidate) <= max_chars:
                                current = candidate
                            else:
                                chunks.append(current)
                                current = fragment
                        else:
                            current = fragment
                    continue
                candidate = f"{current} {sentence}".strip() if current else sentence
                if current and len(candidate) > max_chars:
                    chunks.append(current)
                    current = sentence
                else:
                    current = candidate

        for paragraph in paragraphs:
            add_piece(paragraph)
        if current:
            chunks.append(current)
        return chunks

    @lru_cache(maxsize=512)
    def _translate_chunk(self, text: str) -> str:
        response = self._get_client().text.translate(
            input=text,
            source_language_code="en-IN",
            target_language_code="mni-IN",
            model="sarvam-translate:v1",
        )
        translated = getattr(response, "translated_text", "")
        if not isinstance(translated, str) or not translated.strip():
            raise RuntimeError("Sarvam returned an empty translation")
        return translated.strip()

    def translate_english_to_manipuri_mtei(self, text: str) -> str:
        text = str(text or "").strip()
        if not text:
            return ""
        chunks = self._split_text(text, self.MAX_CHARS)
        if not chunks:
            return ""
        if len(chunks) > 1:
            logger.info(
                "Sarvam translation chunking | Source chars: %s | Chunks: %s",
                len(text), len(chunks)
            )
        translated_chunks = []
        for index, chunk in enumerate(chunks, start=1):
            try:
                translated_chunks.append(self._translate_chunk(chunk))
            except Exception:
                logger.exception(
                    "Sarvam translation chunk %s/%s failed",
                    index, len(chunks)
                )
                # Raise so TranslationService can use its existing NLLB fallback
                # for the complete response rather than mixing languages/scripts.
                raise
        return "\n\n".join(translated_chunks).strip()

sarvam_translation_service = SarvamTranslationService()
