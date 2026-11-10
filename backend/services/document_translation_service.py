import re
import time
import logging
logger = logging.getLogger(__name__)
from fastapi import HTTPException
from backend.document_processing.document_loader import document_loader
from backend.services.translation_service import TranslationService
class DocumentTranslationService:
    """Translate complete text-based documents using the existing translator."""
    def __init__(self):
        self.translator = TranslationService()

    @staticmethod
    def split_text(text: str, max_chars: int = 1200) -> list[str]:
        """Create larger chunks while preserving text order."""
        chunks = []

        paragraphs = re.split(r"\n\s*\n", text)

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            sentences = re.split(r"(?<=[.!?।])\s+", paragraph)
            current = ""

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Split unusually long sentences at word boundaries.
                if len(sentence) > max_chars:
                    if current:
                        chunks.append(current)
                        current = ""

                    words = sentence.split()
                    piece = ""
                    for word in words:
                        candidate = f"{piece} {word}".strip()
                        if piece and len(candidate) > max_chars:
                            chunks.append(piece)
                            piece = word
                        else:
                            piece = candidate
                    if piece:
                        current = piece
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

    def translate_file(
        self,
        file_path: str,
        source_language: str,
        target_language: str,
    ) -> str:
        try:
            text = document_loader.load_preserving_structure(file_path)
            if not text.strip():
                raise ValueError(

                    "No readable text found. The PDF may be scanned."
                )
            chunks = self.split_text(text)
            logger.info(
                "Document translation started | Characters: %s | Chunks: %s",
                len(text),
                len(chunks),
            )

            translation_started = time.perf_counter()

            # Batch-compatible routes use one model inference for up to 8 chunks.
            # The central service falls back to the existing per-chunk path for
            # special routes, preserving their current behavior.
            translated_chunks = self.translator.translate_batch(
                chunks,
                source_language=source_language,
                target_language=target_language,
                batch_size=8,
            )

            if len(translated_chunks) != len(chunks):
                raise ValueError(
                    "Translation returned an unexpected number of document chunks."
                )

            for index, translated in enumerate(translated_chunks, start=1):
                if not translated or not translated.strip():
                    raise ValueError(
                        f"Translation returned empty output for chunk {index}."
                    )

            logger.info(
                "Document translation completed | Chunks: %s | Seconds: %.2f",
                len(chunks),
                time.perf_counter() - translation_started,
            )
            return "\n\n".join(translated_chunks)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Document translation failed: {exc}",
            ) from exc


document_translation_service = DocumentTranslationService()
