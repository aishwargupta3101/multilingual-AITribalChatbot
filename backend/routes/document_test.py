from fastapi import APIRouter

from backend.document_processing.document_loader import document_loader
router = APIRouter()
@router.get("/document-test")
async def document_test(file_path :str):
    text = document_loader.load(
        file_path
    )
    return {
        "characters": len(text),
        "preview": text[:500]
    }