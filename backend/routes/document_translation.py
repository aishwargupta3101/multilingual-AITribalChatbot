import os
import tempfile
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.document_processing.docx_translator import DOCXTranslator
from backend.document_processing.pdf_translator import PDFTranslator
from backend.services.document_translation_service import (
    document_translation_service,
)

router = APIRouter(
    prefix="/document-translation",
    tags=["Document Translation"],
)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _remove_file(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


@router.post("/")
async def translate_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
):
    original_name = Path(file.filename or "document").name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are supported.",
        )

    input_path = None
    output_path = None
    total_size = 0

    try:
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            input_path = temp_file.name
            while True:
                chunk = await file.read(64 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 10 MB limit.",
                    )
                temp_file.write(chunk)

        translator = document_translation_service.translator

        if extension == ".pdf":
            output_extension = ".pdf"
            media_type = "application/pdf"
            with tempfile.NamedTemporaryFile(suffix=output_extension, delete=False) as out:
                output_path = out.name
            PDFTranslator.translate_pdf(
                input_path=input_path,
                output_path=output_path,
                translator=translator,
                source_language=source_language,
                target_language=target_language,
            )

        elif extension == ".docx":
            output_extension = ".docx"
            media_type = (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
            with tempfile.NamedTemporaryFile(suffix=output_extension, delete=False) as out:
                output_path = out.name
            DOCXTranslator.translate_docx(
                input_path=input_path,
                output_path=output_path,
                translator=translator,
                source_language=source_language,
                target_language=target_language,
            )

        else:
            translated_text = document_translation_service.translate_file(
                file_path=input_path,
                source_language=source_language,
                target_language=target_language,
            )
            output_extension = ".txt"
            media_type = "text/plain; charset=utf-8"
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=output_extension,
                delete=False, newline=""
            ) as out:
                output_path = out.name
                out.write(translated_text)

        output_name = f"{Path(original_name).stem}_{target_language}{output_extension}"
        background_tasks.add_task(_remove_file, output_path)
        return FileResponse(
            path=output_path,
            media_type=media_type,
            filename=output_name,
            background=background_tasks,
            headers={
                "X-Translated-Filename": quote(output_name),
                "X-Translated-Format": extension.lstrip("."),
            },
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Document translation failed: {exc}",
        ) from exc
    finally:
        await file.close()
        if input_path:
            _remove_file(input_path)
