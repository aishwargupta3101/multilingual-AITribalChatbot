import logging
import time
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
        "mni_mtei": "manipuri_mtei",
        "as": "assamese", "asm": "assamese",
        "bn": "bengali", "ben": "bengali",
        "brx": "bodo", "doi": "dogri",
        "gu": "gujarati", "guj": "gujarati",
        "kn": "kannada", "kan": "kannada",
        "ks": "kashmiri", "kas": "kashmiri",
        "kas_deva": "kashmiri_deva",
        "gom": "konkani", "mai": "maithili",
        "ml": "malayalam", "mal": "malayalam",
        "mr": "marathi", "mar": "marathi",
        "ne": "nepali", "npi": "nepali",
        "or": "odia", "ory": "odia",
        "pa": "punjabi", "pan": "punjabi",
        "sa": "sanskrit", "san": "sanskrit",
        "sd": "sindhi", "snd": "sindhi",
        "snd_deva": "sindhi_deva",
        "ta": "tamil", "tam": "tamil",
        "te": "telugu", "tel": "telugu",
        "ur": "urdu",
        "sat": "santali", "sat_olck": "santali"
    }

    # Languages verified by the project's live English -> target -> English
    # smoke test. Keep Manipuri Meitei Mayek registered as before; its existing
    # conversion branch below is intentionally unchanged.
    SUPPORTED_LANGUAGES = {
        "english", "hindi", "manipuri", "manipuri_mtei",
        "assamese", "bengali", "bodo", "dogri", "gujarati",
        "kannada", "kashmiri", "kashmiri_deva", "konkani",
        "maithili", "malayalam", "marathi", "nepali", "odia",
        "punjabi", "sanskrit", "santali", "sindhi",
        "sindhi_deva", "tamil", "telugu", "urdu"
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
        logger.info(
            "TRANSLATION DEBUG | "
            "language=%s | supported=%s | module=%s",
            language,
            language in cls.SUPPORTED_LANGUAGES,
            __file__
        )

        if language not in cls.SUPPORTED_LANGUAGES:
            logger.error(
                "Unsupported language: %s | Registered languages: %s",
                language,
                sorted(cls.SUPPORTED_LANGUAGES)
            )
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
        _translation_started = time.perf_counter()
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
            result = self._translate_cached(
                text,
                source_language,
                target_language
            )
            logger.info(
                "TranslationService timing | %s -> %s | source_chars=%s | output_chars=%s | seconds=%.3f | cache=%s",
                source_language, target_language, len(text), len(result or ""),
                time.perf_counter() - _translation_started,
                self._translate_cached.cache_info()
            )
            return result
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

    def _translate_direct_indic_items(self, items, source_language, target_language):
        """
        Translate independent prose items in small batches.

        Long items are split at sentence/word boundaries to avoid the fixed
        input/output limits of a single IndicTrans2 generation call. Leading
        and trailing whitespace are retained when rebuilding each item.
        """
        expanded_chunks = []
        reconstruction = []

        for item in items:
            item = str(item or "")
            leading_length = len(item) - len(item.lstrip())
            trailing_length = len(item) - len(item.rstrip())
            leading = item[:leading_length]
            trailing = item[len(item) - trailing_length:] if trailing_length else ""
            core_end = len(item) - trailing_length if trailing_length else len(item)
            core = item[leading_length:core_end]

            chunks = self._split_translation_chunks(core, max_chars=280)
            if not chunks:
                reconstruction.append(("literal", item))
                continue

            start = len(expanded_chunks)
            expanded_chunks.extend(chunks)
            reconstruction.append(("translated", start, len(expanded_chunks), leading, trailing))

        if not expanded_chunks:
            return [entry[1] if entry[0] == "literal" else "" for entry in reconstruction]

        translated_chunks = self.indictrans.translate_batch(
            expanded_chunks,
            source_language,
            target_language,
            batch_size=4
        )

        if len(translated_chunks) != len(expanded_chunks):
            raise ValueError(
                "IndicTrans2 returned an unexpected number of translated chunks."
            )

        rebuilt_items = []
        for entry in reconstruction:
            if entry[0] == "literal":
                rebuilt_items.append(entry[1])
                continue
            _, start, end, leading, trailing = entry
            translated_core = " ".join(
                str(value or "").strip()
                for value in translated_chunks[start:end]
            ).strip()
            if not translated_core:
                raise ValueError("IndicTrans2 returned an empty translated chunk.")
            rebuilt_items.append(leading + translated_core + trailing)

        return rebuilt_items

    def _translate_long_direct_text(self, text, source_language, target_language):
        """Translate long direct Indic text in bounded chunks, retaining paragraphs."""
        # Keep paragraph separators exactly as supplied.
        parts = re.split(r"(\n[ \t]*\n)", text)
        prose_positions = [
            index for index, part in enumerate(parts)
            if part and not re.fullmatch(r"\n[ \t]*\n", part)
        ]
        if not prose_positions:
            return text

        prose_items = [parts[index] for index in prose_positions]
        translated_items = self._translate_direct_indic_items(
            prose_items, source_language, target_language
        )
        for index, translated in zip(prose_positions, translated_items):
            parts[index] = translated
        return "".join(parts)

    @staticmethod
    def _markdown_line_parts(line):
        """Return the Markdown line prefix and body without altering syntax."""
        match = re.match(
            r"^([ \t]*(?:#{1,6}[ \t]+|>[ \t]?|[-+*][ \t]+|\d+[.)][ \t]+)?)",
            line,
        )
        prefix = match.group(1) if match else ""
        return prefix, line[len(prefix):]

    @staticmethod
    def _translate_markdown_inline(body, source_language, target_language, translate):
        """Translate only prose spans; retain Markdown syntax/code/URLs verbatim."""
        syntax = re.compile(
            r"```.*?```|`[^`]*`|"
            r"!\[[^\]]*\]\([^)]*\)|\[[^\]]*\]\([^)]*\)|"
            r"https?://[^\s)]+|"
            r"</?[A-Za-z][^>]*>|"
            r"\*\*|__|~~|[*_`~]|\|",
            re.DOTALL,
        )

        pieces = []
        cursor = 0

        def translate_prose(prose):
            if not prose or not re.search(r"\w", prose, flags=re.UNICODE):
                return prose
            return translate(prose, source_language, target_language)

        for match in syntax.finditer(body):
            if match.start() > cursor:
                pieces.append(translate_prose(body[cursor:match.start()]))
            pieces.append(match.group(0))
            cursor = match.end()

        if cursor < len(body):
            pieces.append(translate_prose(body[cursor:]))

        return "".join(pieces)

    def _translate_markdown_response(self, text, source_language, target_language):
        """Translate Markdown prose in batches while preserving source structure."""
        syntax = re.compile(
            r"```.*?```|`[^`]*`|"
            r"!\[[^\]]*\]\([^)]*\)|\[[^\]]*\]\([^)]*\)|"
            r"https?://[^\s)]+|"
            r"</?[A-Za-z][^>]*>|"
            r"\*\*|__|~~|[*_`~]|\|",
            re.DOTALL,
        )

        # Keep a reconstruction plan so translations can be batched without moving
        # Markdown syntax, code, links, URLs, line prefixes, or blank lines.
        plan = []
        prose_items = []
        in_fence = False
        fence_marker = None

        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith(("```", "~~~")):
                marker = stripped[:3]
                if not in_fence:
                    in_fence = True
                    fence_marker = marker
                elif marker == fence_marker:
                    in_fence = False
                    fence_marker = None
                plan.append(("literal", line))
                continue

            if in_fence or not line.strip():
                plan.append(("literal", line))
                continue

            if re.fullmatch(r"[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*", line):
                plan.append(("literal", line))
                continue

            prefix, body = self._markdown_line_parts(line)
            segments = [("literal", prefix)]
            cursor = 0
            for match in syntax.finditer(body):
                if match.start() > cursor:
                    prose = body[cursor:match.start()]
                    if re.search(r"\w", prose, flags=re.UNICODE):
                        index = len(prose_items)
                        prose_items.append(prose)
                        segments.append(("prose", index))
                    else:
                        segments.append(("literal", prose))
                segments.append(("literal", match.group(0)))
                cursor = match.end()

            if cursor < len(body):
                prose = body[cursor:]
                if re.search(r"\w", prose, flags=re.UNICODE):
                    index = len(prose_items)
                    prose_items.append(prose)
                    segments.append(("prose", index))
                else:
                    segments.append(("literal", prose))
            plan.append(("segments", segments))

        if not prose_items:
            literal_lines = []
            for kind, value in plan:
                if kind == "literal":
                    literal_lines.append(value)
                else:
                    literal_lines.append("".join(
                        segment_value
                        for segment_kind, segment_value in value
                        if segment_kind == "literal"
                    ))
            return "\n".join(literal_lines)

        # Direct IndicTrans2 routes can translate many independent prose spans
        # in one inference batch. Keep the existing route for Manipuri and
        # Meitei Mayek, whose specialized conversion/intermediate paths must
        # remain untouched.
        direct_indic_route = (
            source_language not in {"manipuri", "manipuri_mtei"}
            and target_language not in {"manipuri", "manipuri_mtei"}
        )
        if direct_indic_route and hasattr(self.indictrans, "translate_batch"):
            translated_items = self._translate_direct_indic_items(
                prose_items, source_language, target_language
            )
        else:
            translated_items = [
                self.translate(item, source_language, target_language)
                for item in prose_items
            ]

        output_lines = []
        for kind, value in plan:
            if kind == "literal":
                output_lines.append(value)
                continue
            rebuilt = []
            for segment_kind, segment_value in value:
                if segment_kind == "literal":
                    rebuilt.append(segment_value)
                else:
                    rebuilt.append(translated_items[segment_value])
            output_lines.append("".join(rebuilt))
        return "\n".join(output_lines)

    def translate_response(self, text, target_language, source_language="english"):
        """Translate response prose while preserving Markdown and code formatting."""
        text = self._validate_text(text)
        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)

        self.validate_language(source_language)
        self.validate_language(target_language)

        if not text or source_language == target_language:
            return text

        # Keep the dedicated Meitei Mayek conversion path unchanged.
        if source_language == "manipuri_mtei" or target_language == "manipuri_mtei":
            return self.translate(text, source_language, target_language)

        has_markdown = (
            "\n" in text
            or bool(re.search(r"(^|\s)(#{1,6}\s|[-+*]\s|\d+[.)]\s|>\s|`|\*\*|__|~~)", text))
        )
        if not has_markdown:
            direct_indic_route = (
                source_language not in {"manipuri", "manipuri_mtei"}
                and target_language not in {"manipuri", "manipuri_mtei"}
            )
            if direct_indic_route and len(text) > 280:
                return self._translate_long_direct_text(
                    text, source_language, target_language
                )
            return self.translate(text, source_language, target_language)

        return self._translate_markdown_response(
            text, source_language, target_language
        )

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

        direct_indic_route = (
            source_language not in {"manipuri", "manipuri_mtei"}
            and target_language not in {"manipuri", "manipuri_mtei"}
        )
        if direct_indic_route and len(text) > 280:
            translated = self._translate_long_direct_text(
                text, source_language, target_language
            )
            logger.info(
                "Voice direct-Indic chunking completed | source_chars=%s | output_chars=%s",
                len(text),
                len(translated),
            )
            return translated

        return self.translate(text, source_language, target_language)

    def clear_cache(self):
        self._translate_cached.cache_clear()
        self.indictrans.clear_cache()
        self.nllb.clear_cache()
        logger.info("Translation caches cleared.")

translation_service = TranslationService()
