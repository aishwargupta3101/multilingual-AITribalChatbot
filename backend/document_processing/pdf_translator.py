import logging
import os
from pathlib import Path
from typing import Any

import pymupdf

logger = logging.getLogger(__name__)


class PDFTranslator:
    """Best-effort PDF text replacement with Unicode font support."""

    FONT_ENV_BY_LANGUAGE = {
        language: f"TRIBAL_PDF_FONT_{suffix}"
        for suffix, languages in {
            "DEVANAGARI": ("hindi", "bodo", "dogri", "kashmiri_deva", "maithili", "marathi", "nepali", "sanskrit", "santali"),
            "BENGALI": ("assamese", "bengali", "manipuri"),
            "MEITEI": ("manipuri_mtei",),
            "GUJARATI": ("gujarati",),
            "KANNADA": ("kannada",),
            "MALAYALAM": ("malayalam",),
            "ODIA": ("odia",),
            "GURMUKHI": ("punjabi",),
            "TAMIL": ("tamil",),
            "TELUGU": ("telugu",),
            "ARABIC": ("urdu", "sindhi",),
        }.items() for language in languages
    }

    WINDOWS_FONT_CANDIDATES = {
        "default": [
            r"C:\Windows\Fonts\Nirmala.ttc",
            r"C:\Windows\Fonts\arial.ttf",
        ],
    }
    @staticmethod
    def _rgb(color: int) -> tuple[float, float, float]:
        return (
            ((color >> 16) & 255) / 255,
            ((color >> 8) & 255) / 255,
            (color & 255) / 255,
        )

    @classmethod
    def _find_font(cls, target_language: str) -> str:
        language = (target_language or "").lower().strip()
        env_key = cls.FONT_ENV_BY_LANGUAGE.get(language)
        candidates = []
        if env_key:
            configured = os.getenv(env_key)
            if configured:
                candidates.append(configured)

        candidates.extend(cls.WINDOWS_FONT_CANDIDATES.get(
            language, cls.WINDOWS_FONT_CANDIDATES["default"]
        ))

        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return str(Path(candidate))

        raise FileNotFoundError(
            "No suitable Unicode font file was found for target language "
            f"'{language}'. Set the appropriate font environment variable "
            "to a .ttf or .otf font that supports the target script. "
            "Hindi: TRIBAL_PDF_FONT_DEVANAGARI; "
            "Manipuri Bengali: TRIBAL_PDF_FONT_MANIPURI; "
            "Manipuri Meitei Mayek: TRIBAL_PDF_FONT_MEITEI."
        )

    @classmethod
    def _extract_blocks(cls, page: Any) -> list[dict]:
        result = []
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") != 0:
                continue
            lines = block.get("lines", [])
            spans = [
                span for line in lines for span in line.get("spans", [])
                if span.get("text", "").strip()
            ]
            if not spans:
                continue

            text = "\n".join(
                "".join(span.get("text", "") for span in line.get("spans", []))
                for line in lines
            ).strip()
            bbox = block.get("bbox")
            if not text or not bbox or len(bbox) != 4:
                continue

            sizes = [float(span.get("size", 10)) for span in spans]
            result.append({
                "bbox": tuple(float(v) for v in bbox),
                "original_text": text,
                "font_size": max(5.0, min(36.0, sum(sizes) / len(sizes))),
                "color": cls._rgb(int(spans[0].get("color", 0))),
            })
        return result

    @staticmethod
    def _insert_text(
        page: Any,
        rect: Any,
        text: str,
        font_size: float,
        color: tuple[float, float, float],
        font_path: str,
        font_name: str,
    ) -> bool:
        if not text.strip():
            return True

        rect = pymupdf.Rect(rect)
        inset = min(1.0, max(0.0, min(rect.width, rect.height) * 0.025))
        rect = pymupdf.Rect(
            rect.x0 + inset, rect.y0 + inset,
            rect.x1 - inset, rect.y1 - inset,
        )
        if rect.width <= 1 or rect.height <= 1:
            return False

        size = font_size
        while size >= 5.0:
            spare = page.insert_textbox(
                rect,
                text,
                fontname=font_name,
                fontfile=font_path,
                fontsize=size,
                color=color,
                align=0,
                lineheight=1.0,
                overlay=True,
            )
            if spare >= 0:
                return True
            size -= 0.5
        return False

    @classmethod
    def create_translated_pdf(
        cls,
        input_path: str,
        output_path: str,
        translated_blocks: list[dict],
        target_language: str = "hindi",
    ) -> str:
        """Create a translated PDF from page-indexed text blocks."""
        source = Path(input_path)
        destination = Path(output_path)
        if not source.is_file():
            raise FileNotFoundError(f"Input PDF not found: {source}")
        if source.resolve() == destination.resolve():
            raise ValueError("Output PDF must differ from input PDF.")

        font_path = cls._find_font(target_language)
        font_name = "TranslatedUnicodeFont"

        pdf = pymupdf.open(str(source))
        try:
            grouped: dict[int, list[dict]] = {}
            for item in translated_blocks:
                if not item.get("original_text", "").strip():
                    continue
                if "translated_text" not in item:
                    raise ValueError("A translated block is missing translated_text.")
                page_number = int(item["page"])
                if not 0 <= page_number < pdf.page_count:
                    raise ValueError(f"Invalid PDF page index: {page_number}")
                rect = pymupdf.Rect(item["bbox"]) & pdf[page_number].rect
                if rect.is_empty or rect.is_infinite:
                    continue
                grouped.setdefault(page_number, []).append({**item, "_rect": rect})

            for page_number, blocks in grouped.items():
                page = pdf[page_number]
                for block in blocks:
                    page.add_redact_annot(block["_rect"], fill=(1, 1, 1))
                page.apply_redactions(images=0, graphics=0, text=0)

                for block in blocks:
                    inserted = cls._insert_text(
                        page=page,
                        rect=block["_rect"],
                        text=str(block.get("translated_text", "")),
                        font_size=float(block.get("font_size", 10.0)),
                        color=tuple(block.get("color", (0, 0, 0))),
                        font_path=font_path,
                        font_name=font_name,
                    )
                    if not inserted:
                        logger.warning(
                            "Translated text did not fit on PDF page %s: %.80r",
                            page_number + 1,
                            block.get("translated_text", ""),
                        )

            destination.parent.mkdir(parents=True, exist_ok=True)
            pdf.save(str(destination), garbage=4, deflate=True)
            return str(destination)
        finally:
            pdf.close()

    @classmethod
    def translate_pdf(
        cls,
        input_path: str,
        output_path: str,
        translator: Any,
        source_language: str,
        target_language: str,
    ) -> str:
        """Translate PDF text blocks with an existing translator instance."""
        pdf = pymupdf.open(input_path)
        blocks = []
        try:
            for page_number, page in enumerate(pdf):
                for block in cls._extract_blocks(page):
                    translated = translator.translate(
                        text=block["original_text"],
                        source_language=source_language,
                        target_language=target_language,
                    )
                    if not translated or not str(translated).strip():
                        raise ValueError(
                            f"Empty translation on PDF page {page_number + 1}."
                        )
                    blocks.append({
                        "page": page_number,
                        "bbox": block["bbox"],
                        "original_text": block["original_text"],
                        "translated_text": str(translated).strip(),
                        "font_size": block["font_size"],
                        "color": block["color"],
                    })
        finally:
            pdf.close()

        return cls.create_translated_pdf(
            input_path=input_path,
            output_path=output_path,
            translated_blocks=blocks,
            target_language=target_language,
        )
