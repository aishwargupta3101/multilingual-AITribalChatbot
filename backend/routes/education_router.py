from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)
from backend.services.pdf_extraction_service import (
    extract_text_from_pdf,
    PDFExtractionError,
)
router = APIRouter(
    prefix="/api/v1/education",
    tags=["Education Assistant"],
)
@router.post("/upload")
async def upload_textbook(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )
    max_file_size = 15 * 1024 * 1024
    contents = await file.read(max_file_size + 1)
    if len(contents) > max_file_size:
        raise HTTPException(
            status_code=413,
            detail="PDF must be smaller than 15 MB.",
        )
    try:
        result = extract_text_from_pdf(contents)
        return {
            "filename": file.filename,
            "page_count": result["page_count"],
            "extracted_pages": result["extracted_pages"],
            "text": result["text"],
        }
    except PDFExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )