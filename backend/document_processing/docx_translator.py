import logging
from pathlib import Path
from typing import Any

from docx import Document

logger = logging.getLogger(__name__)

class DOCXTranslator:
    """
    Translate editable DOCX paragraphs while retaining document structure.

    Paragraph styles, alignment, tables, headers/footers, section settings,
    images, and other non-text elements are retained by editing the existing
    document rather than rebuilding it. Within a translated paragraph, the
    translated text is placed in the first non-empty run; mixed inline
    formatting (for example, bold words inside a sentence) may therefore
    not be preserved exactly.
    """

    @staticmethod
    def _translate_paragraph(paragraph: Any, translator: Any,
                             source_language: str, target_language: str) -> None:
        original = paragraph.text
        if not original or not original.strip():
            return
        logger.info(
            "Translating DOCX paragraph | characters=%s",
            len(original),
        )
        translated = translator.translate(
            text=original,
            source_language=source_language,
            target_language=target_language,
        )
        if not translated or not str(translated).strip():
            raise ValueError(
                f"Translation returned empty output for paragraph: {original[:80]!r}"
            )

        translated = str(translated).strip()
        logger.info(
            "DOCX paragraph translation completed | input_chars=%s",
            len(original),
        )
        runs = paragraph.runs

        if runs:
            # Keep the first run's character style and paragraph-level style.
            first_nonempty = next(
                (run for run in runs if run.text and run.text.strip()),
                runs[0],
            )
            first_nonempty.text = translated
            for run in runs:
                if run is not first_nonempty:
                    run.text = ""
        else:
            # Normally a paragraph with text has at least one run.
            paragraph.add_run(translated)

    @classmethod
    def _translate_table(cls, table: Any, translator: Any,
                         source_language: str, target_language: str) -> None:
        for row in table.rows:
            for cell in row.cells:
                cls._translate_container(
                    cell, translator, source_language, target_language
                )

    @classmethod
    def _translate_container(cls, container: Any, translator: Any,
                             source_language: str, target_language: str) -> None:
        for paragraph in container.paragraphs:
            cls._translate_paragraph(
                paragraph, translator, source_language, target_language
            )
        for table in getattr(container, "tables", []):
            cls._translate_table(
                table, translator, source_language, target_language
            )

    @classmethod
    def translate_docx(
        cls,
        input_path: str,
        output_path: str,
        translator: Any,
        source_language: str,
        target_language: str,
    ) -> str:
        source = Path(input_path)
        destination = Path(output_path)

        if not source.is_file():
            raise FileNotFoundError(f"Input DOCX not found: {source}")
        if source.resolve() == destination.resolve():
            raise ValueError("Output DOCX must differ from input DOCX.")

        document = Document(str(source))

        # Main body paragraphs and tables.
        cls._translate_container(
            document, translator, source_language, target_language
        )

        # Headers and footers can contain repeated text, so translate each
        # section's header/footer content as part of the same document.
        seen_parts = set()
        for section in document.sections:
            for part in (
                section.header,
                section.footer,
                section.first_page_header,
                section.first_page_footer,
                section.even_page_header,
                section.even_page_footer,
            ):
                part_key = str(getattr(part, "part", part).partname)
                if part_key in seen_parts:
                    continue
                seen_parts.add(part_key)
                cls._translate_container(
                    part, translator, source_language, target_language
                )

        destination.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(destination))
        logger.info("Translated DOCX saved to %s", destination)
        return str(destination)
