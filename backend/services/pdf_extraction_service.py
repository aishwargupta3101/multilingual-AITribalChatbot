import fitz
from io import BytesIO


class PDFExtractionError(Exception):
    """Raised when PDF extraction fails."""


def extract_text_from_pdf(
    pdf_bytes: bytes,
    max_pages: int = 100,
) -> dict:
    """
    Extract text from an uploaded PDF.

    Returns:
        {
            "text": extracted text,
            "page_count": number of pages,
            "extracted_pages": pages containing text
        }
    """
    if not pdf_bytes:
        raise PDFExtractionError("The uploaded PDF is empty.")

    try:
        with fitz.open(
            stream=BytesIO(pdf_bytes),
            filetype="pdf",
        ) as document:

            if document.is_encrypted:
                raise PDFExtractionError(
                    "Password-protected PDFs are not supported."
                )

            page_count = len(document)

            if page_count == 0:
                raise PDFExtractionError(
                    "The PDF contains no pages."
                )

            if page_count > max_pages:
                raise PDFExtractionError(
                    f"PDF exceeds the {max_pages}-page limit."
                )

            extracted_pages = []
            page_texts = []

            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()

                if text:
                    extracted_pages.append(page_number)
                    page_texts.append(
                        f"[Page {page_number}]\n{text}"
                    )

            full_text = "\n\n".join(page_texts)

            if not full_text:
                raise PDFExtractionError(
                    "No readable text found. "
                    "This may be a scanned PDF."
                )
            return {
                "text": full_text,
                "page_count": page_count,
                "extracted_pages": extracted_pages,
            }
    except PDFExtractionError:
        raise
    except Exception as exc:
        raise PDFExtractionError(
            f"Unable to process PDF: {exc}"
        ) from exc